// Reimplementation of `sample_chunked_data.py`, since I got OOM with large
// corpora.

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <optional>
#include <random>

std::string get_file_contents(const char *filename) {
  std::ifstream in(filename, std::ios::in | std::ios::binary);

  if (!in)
    throw std::runtime_error(std::string("failed to open file `") + filename +
        "'");

  in.seekg(0, std::ios::end);

  std::string contents;
  contents.resize(in.tellg());

  in.seekg(0, std::ios::beg);
  in.read(&contents[0], contents.size());
  
  return contents;
}

static const std::string EOF_SYMBOL = "▗";

// Scan through the corpus string, building two vectors of identical lengths.
// The corpus contains the concatenation of multiple files, which are separated
// by the special word `EOF_SYMBOL`.
//
// `word_starts` will contain the indices in the corpus at which a new word
// starts. We use a vector of indices here so that we do not need to have a
// separate `std::string` per word (with which I got OOM on a large corpus).
//
// `file_lengths` will contain for each word the number of words remaining in
// the current file. This vector will be used to identify positions at which a
// full chunk can be sampled without crossing files.
size_t parse_words_and_lengths(const std::string& corpus,
    std::vector<size_t>& word_starts,
    std::vector<size_t>& file_lengths) {
  size_t n_files = 0;

  std::optional<size_t> word_start = std::nullopt;

  for (size_t i = 0; i < corpus.size(); i++) {
    //if (corpus[i] == '\t' || corpus[i] == '\r')
      //throw std::runtime_error("invalid whitespace at position " + std::to_string(i));

    bool is_white = (corpus[i] == '\n' || corpus[i] == ' ');

    if (!word_start && !is_white) {
      // A new word starts at this position.
      word_start = i;
    } else if (word_start && is_white) {
      // We have a finished word.
      word_starts.push_back(*word_start);
      file_lengths.push_back(0);

      // Check if we have reached the end of the current file.
      bool isEOF = false;
      if (i - *word_start >= EOF_SYMBOL.size()) {
        isEOF = true;
        for (size_t j = 0; j < EOF_SYMBOL.size(); j++)
          isEOF = isEOF && corpus[*word_start + j] == EOF_SYMBOL[j];
      }

      // If we have reached the end of the file, write the number of remaining
      // words for the words in this file backwards.
      if (isEOF) {
        size_t k = word_starts.size() - 1;
        size_t length = 1;

        while (file_lengths[k] == 0) {
          file_lengths[k] = length++;

          if (k-- == 0)
            break;
        }

        n_files++;
      }

      word_start = std::nullopt;
    }
  }

  return n_files;
}

void write_word(const std::string& corpus,
    size_t start,
    std::ostream& out) {
  for (size_t i = start;
       i < corpus.size() && corpus[i] != '\n' && corpus[i] != ' ';
       i++)
    out << corpus[i];
}

size_t myrand(size_t n) {
  static std::random_device rd;
  static std::mt19937 gen(rd());

  std::uniform_int_distribution<size_t> dis(0, n);
  return dis(gen);
}

void sample_chunk(const std::string& corpus,
    const std::vector<size_t>& word_starts,
    const std::vector<size_t>& file_lengths,
    size_t sample_size,
    std::ostream& out) {
  for(;;) {
    size_t k = myrand(word_starts.size() - 1);

    if (file_lengths[k] >= sample_size) {
      for (size_t i = 0; i < sample_size; i++) {
        write_word(corpus, word_starts[k+i], out);
        if (i + 1 < sample_size)
          out << ' ';
      }

      return;
    }
  }
}

int main(int argc, const char** argv) {
  if (argc != 4) {
    std::cerr << "Randomly sample chunks of training data from a concatenated "
      << "corpus.\n\n"
      << "The corpus is read into memory from the file before sampling.\n"
      << "Generated samples are written line-by-line to stdout, with a fixed\n"
      << "number of symbols per line. Samples do not cross files.\n\n"
      << "This tool is a hack to work around the fact that OpenNMT-tf does\n"
      << "not support sampling in this way during training (AFAIK).\n\n"
      << "usage: " << argv[0] << " CORPUS SAMPLE_SIZE NUM_SAMPLES" 
			<< std::endl;
    return 1;
  }

  std::cerr << "Reading corpus into memory from `" << argv[1] << "'..."
    << std::endl;
  
  std::string corpus = get_file_contents(argv[1]);

  std::cerr << "Done.\nParsing corpus into words..." << std::endl;

  std::vector<size_t> word_starts;
  std::vector<size_t> file_lengths;
  size_t n_files = parse_words_and_lengths(corpus, word_starts, file_lengths);

  std::cerr << "Done. Read " << word_starts.size() << " words "
    << "in " << n_files << " files." << std::endl;

  size_t sample_size = std::stoi(argv[2]);
  size_t num_samples = std::stoi(argv[3]);

  /*for (size_t i = 0; i < word_starts.size(); i++) {
    write_word(corpus, word_starts[i], std::cout);
    std::cout << '\t' << file_lengths[i] << std::endl;
  }
  return 0;*/

  std::cerr << "Sampling " << num_samples << " chunks of size " << sample_size
    << "..." << std::endl;

  for (size_t i = 0; i < num_samples; i++) {
    sample_chunk(corpus, word_starts, file_lengths, sample_size, std::cout);
    std::cout << '\n';
  }

  std::cerr << "All done." << std::endl;

  return 0;
}
