%{
#include <stdio.h>
%}

%option noyywrap
%option yylineno

%%

"CLOUD"       { printf("TOKEN: CLOUD\n"); }
"SERVER"      { printf("TOKEN: SERVER\n"); }
"DATABASE"    { printf("TOKEN: DATABASE\n"); }
"CPU"         { printf("TOKEN: CPU\n"); }
"MEMORY"      { printf("TOKEN: MEMORY\n"); }
"STORAGE"     { printf("TOKEN: STORAGE\n"); }
"REGION"      { printf("TOKEN: REGION\n"); }

"MB"          { printf("TOKEN: UNIT( MB )\n"); }
"GB"          { printf("TOKEN: UNIT( GB )\n"); }
"TB"          { printf("TOKEN: UNIT( TB )\n"); }

"{"           { printf("TOKEN: LBRACE\n"); }
"}"           { printf("TOKEN: RBRACE\n"); }


[0-9]+        { printf("TOKEN: NUMBER(%s)\n", yytext); }


[A-Za-z_][A-Za-z0-9_-]* {
    printf("TOKEN: IDENTIFIER(%s)\n", yytext);
}

"#"[^\r\n]*  { }


[ \t\r\n]+    { }


. {
    printf("LEXICAL_ERROR: line %d: unexpected character '%s'\n",
           yylineno, yytext);
}

%%

int main(void)
{
    yylex();
    return 0;
}