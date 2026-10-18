#ifndef CLARA_PARSER_H
#define CLARA_PARSER_H

#include <stdio.h>
#include "ast/ast.h"
#include "tokens.h"

typedef struct Parser Parser;

/* Creates a parser instance for the given open file stream. */
Parser *parser_create(FILE *input);

/* Destroys the parser instance and frees internal buffers. */
void parser_destroy(Parser *parser);

/* Parses the input stream and constructs the AST. Returns NULL on syntax error. */
ASTNode *parser_parse(Parser *parser);

/* Returns the total count of syntax/lexical errors encountered during parsing. */
int parser_error_count(const Parser *parser);

/* Convenience function to parse a source file directly by path.
 * If error_count is non-NULL, writes the error count to it.
 * Returns root ASTNode* on success, or NULL on failure. */
ASTNode *clara_parse_file(const char *filepath, int *error_count);

#endif
