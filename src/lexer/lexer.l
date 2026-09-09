%{
#include <stdio.h>
#include "tokens.h"
%}

%option noyywrap
%option yylineno

%%

"CLOUD" {
    printf("TOKEN_CLOUD\n");
    return TOKEN_CLOUD;
}

"SERVER" {
    printf("TOKEN_SERVER\n");
    return TOKEN_SERVER;
}

"DATABASE" {
    printf("TOKEN_DATABASE\n");
    return TOKEN_DATABASE;
}

"CPU" {
    printf("TOKEN_CPU\n");
    return TOKEN_CPU;
}

"MEMORY" {
    printf("TOKEN_MEMORY\n");
    return TOKEN_MEMORY;
}

"STORAGE" {
    printf("TOKEN_STORAGE\n");
    return TOKEN_STORAGE;
}

"REGION" {
    printf("TOKEN_REGION\n");
    return TOKEN_REGION;
}

"MB" {
    printf("TOKEN_UNIT(%s)\n", yytext);
    return TOKEN_UNIT;
}

"GB" {
    printf("TOKEN_UNIT(%s)\n", yytext);
    return TOKEN_UNIT;
}

"TB" {
    printf("TOKEN_UNIT(%s)\n", yytext);
    return TOKEN_UNIT;
}

"{" {
    printf("TOKEN_LBRACE\n");
    return TOKEN_LBRACE;
}

"}" {
    printf("TOKEN_RBRACE\n");
    return TOKEN_RBRACE;
}

[0-9]+ {
    printf("TOKEN_NUMBER(%s)\n", yytext);
    return TOKEN_NUMBER;
}

[A-Za-z_][A-Za-z0-9_-]* {
    printf("TOKEN_IDENTIFIER(%s)\n", yytext);
    return TOKEN_IDENTIFIER;
}

"#"[^\r\n]* {
}

[ \t\r\n]+ {
}

. {
    printf(
        "LEXICAL_ERROR: line %d: unexpected character '%s'\n",
        yylineno,
        yytext
    );
    return TOKEN_LEXICAL_ERROR;
}

<<EOF>> {
    return TOKEN_EOF;
}

%%

int main(void)
{
    int token;

    do
    {
        token = yylex();
    }
    while (token != TOKEN_EOF &&
           token != TOKEN_LEXICAL_ERROR);

    return 0;
}