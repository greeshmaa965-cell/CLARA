%{
#include <stdio.h>
%}

%option noyywrap
%option yylineno

%%

/* ---------- CLARA Keywords ---------- */

"CLOUD"       { printf("TOKEN: CLOUD\n"); }
"SERVER"      { printf("TOKEN: SERVER\n"); }
"DATABASE"    { printf("TOKEN: DATABASE\n"); }
"CPU"         { printf("TOKEN: CPU\n"); }
"MEMORY"      { printf("TOKEN: MEMORY\n"); }
"STORAGE"     { printf("TOKEN: STORAGE\n"); }
"REGION"      { printf("TOKEN: REGION\n"); }


/* ---------- Units ---------- */

"MB"          { printf("TOKEN: UNIT( MB )\n"); }
"GB"          { printf("TOKEN: UNIT( GB )\n"); }
"TB"          { printf("TOKEN: UNIT( TB )\n"); }


/* ---------- Braces ---------- */

"{"           { printf("TOKEN: LBRACE\n"); }
"}"           { printf("TOKEN: RBRACE\n"); }


/* ---------- Numbers ---------- */

[0-9]+        { printf("TOKEN: NUMBER(%s)\n", yytext); }


/* ---------- Identifiers ---------- */

[A-Za-z_][A-Za-z0-9_-]* {
    printf("TOKEN: IDENTIFIER(%s)\n", yytext);
}


/* ---------- Comments ---------- */

"#"[^\r\n]*  { }


/* ---------- Whitespace ---------- */

[ \t\r\n]+    { }


/* ---------- Invalid Characters ---------- */

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