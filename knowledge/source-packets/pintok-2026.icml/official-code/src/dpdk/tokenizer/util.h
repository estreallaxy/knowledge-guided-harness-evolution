// util.h
#ifndef UTIL_H
#define UTIL_H

// Loads and parses your JSON file. 0 on success, –1 on failure.
int read_json_dictionary(const char *json_file);

// Looks up a word in the dictionary and returns its token ID
int lookup_token(const char *word);

#endif // UTIL_H