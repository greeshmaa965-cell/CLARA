%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tokens.h"

int clara_lexer_verbose = 0;

const char *token_type_name(TokenType type)
{
    switch (type)
    {
        case TOKEN_CLOUD:          return "CLOUD";
        case TOKEN_SERVER:         return "SERVER";
        case TOKEN_DATABASE:       return "DATABASE";
        case TOKEN_CPU:            return "CPU";
        case TOKEN_MEMORY:         return "MEMORY";
        case TOKEN_STORAGE:        return "STORAGE";
        case TOKEN_REGION:         return "REGION";
        case TOKEN_IDENTIFIER:     return "IDENTIFIER";
        case TOKEN_NUMBER:         return "NUMBER";
        case TOKEN_UNIT:           return "UNIT";
        case TOKEN_LBRACE:         return "{";
        case TOKEN_RBRACE:         return "}";
        case TOKEN_EOF:            return "EOF";
        case TOKEN_LEXICAL_ERROR:  return "LEXICAL_ERROR";
        default:                   return "UNKNOWN_TOKEN";
    }
}

void clara_lexer_reset(void)
{
    yylineno = 1;
}
%}

%option noyywrap
%option yylineno

%%

"CLOUD" {
    if (clara_lexer_verbose) printf("TOKEN_CLOUD\n");
    return TOKEN_CLOUD;
}

"SERVER" {
    if (clara_lexer_verbose) printf("TOKEN_SERVER\n");
    return TOKEN_SERVER;
}

"DATABASE" {
    if (clara_lexer_verbose) printf("TOKEN_DATABASE\n");
    return TOKEN_DATABASE;
}

"CPU" {
    if (clara_lexer_verbose) printf("TOKEN_CPU\n");
    return TOKEN_CPU;
}

"MEMORY" {
    if (clara_lexer_verbose) printf("TOKEN_MEMORY\n");
    return TOKEN_MEMORY;
}

"STORAGE" {
    if (clara_lexer_verbose) printf("TOKEN_STORAGE\n");
    return TOKEN_STORAGE;
}

"REGION" {
    if (clara_lexer_verbose) printf("TOKEN_REGION\n");
    return TOKEN_REGION;
}

"MB" {
    if (clara_lexer_verbose) printf("TOKEN_UNIT(%s)\n", yytext);
    return TOKEN_UNIT;
}

"GB" {
    if (clara_lexer_verbose) printf("TOKEN_UNIT(%s)\n", yytext);
    return TOKEN_UNIT;
}

"TB" {
    if (clara_lexer_verbose) printf("TOKEN_UNIT(%s)\n", yytext);
    return TOKEN_UNIT;
}

"{" {
    if (clara_lexer_verbose) printf("TOKEN_LBRACE\n");
    return TOKEN_LBRACE;
}

"}" {
    if (clara_lexer_verbose) printf("TOKEN_RBRACE\n");
    return TOKEN_RBRACE;
}

[0-9]+ {
    if (clara_lexer_verbose) printf("TOKEN_NUMBER(%s)\n", yytext);
    return TOKEN_NUMBER;
}

[A-Za-z_][A-Za-z0-9_-]* {
    if (clara_lexer_verbose) printf("TOKEN_IDENTIFIER(%s)\n", yytext);
    return TOKEN_IDENTIFIER;
}

"#"[^\r\n]* {
}

[ \t\r\n]+ {
}

. {
    fprintf(
        stderr,
        "Lexical error: line %d: unexpected character '%s'\n",
        yylineno,
        yytext
    );
    return TOKEN_LEXICAL_ERROR;
}

<<EOF>> {
    return TOKEN_EOF;
}

%%

#ifdef CLARA_LEXER_STANDALONE
int main(void)
{
    int token;
    clara_lexer_verbose = 1;

    do
    {
        token = yylex();
    }
    while (token != TOKEN_EOF &&
           token != TOKEN_LEXICAL_ERROR);

    return 0;
}
#endif