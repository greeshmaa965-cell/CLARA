#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tokens.h"
#include "ast/ast.h"
#include "parser/parser.h"
#include "semantic/semantic.h"

#define CLARA_VERSION "0.2.0-dev"

static void print_usage(const char *progname)
{
    printf("CLARA Compiler (v%s)\n", CLARA_VERSION);
    printf("Cloud Language, Analysis, and Resource Architecture\n\n");
    printf("Usage: %s [options] <file.clara>\n\n", progname);
    printf("Options:\n");
    printf("  --ast       Print the Abstract Syntax Tree (AST)\n");
    printf("  --check     Perform syntax and semantic verification only\n");
    printf("  --tokens    Print the lexer token stream\n");
    printf("  -v, --version Display compiler version\n");
    printf("  -h, --help    Display this help message\n");
}

int main(int argc, char **argv)
{
    const char *filepath = NULL;
    int show_ast = 0;
    int check_only = 0;
    int show_tokens = 0;
    int arg_index;

    if (argc < 2)
    {
        print_usage(argv[0]);
        return 1;
    }

    for (arg_index = 1; arg_index < argc; arg_index++)
    {
        if (strcmp(argv[arg_index], "-h") == 0 || strcmp(argv[arg_index], "--help") == 0)
        {
            print_usage(argv[0]);
            return 0;
        }
        else if (strcmp(argv[arg_index], "-v") == 0 || strcmp(argv[arg_index], "--version") == 0)
        {
            printf("CLARA version %s\n", CLARA_VERSION);
            return 0;
        }
        else if (strcmp(argv[arg_index], "--ast") == 0)
        {
            show_ast = 1;
        }
        else if (strcmp(argv[arg_index], "--check") == 0)
        {
            check_only = 1;
        }
        else if (strcmp(argv[arg_index], "--tokens") == 0)
        {
            show_tokens = 1;
        }
        else if (argv[arg_index][0] == '-')
        {
            fprintf(stderr, "Unknown option: %s\n", argv[arg_index]);
            print_usage(argv[0]);
            return 1;
        }
        else
        {
            filepath = argv[arg_index];
        }
    }

    if (filepath == NULL)
    {
        fprintf(stderr, "Error: no input file specified.\n\n");
        print_usage(argv[0]);
        return 1;
    }

    if (show_tokens)
    {
        FILE *f = fopen(filepath, "r");
        if (!f)
        {
            fprintf(stderr, "Error: cannot open '%s'\n", filepath);
            return 1;
        }
        extern FILE *yyin;
        extern int yylex(void);
        extern char *yytext;
        extern void clara_lexer_reset(void);
        extern int clara_lexer_verbose;

        clara_lexer_reset();
        yyin = f;
        clara_lexer_verbose = 1;
        int tok;
        do
        {
            tok = yylex();
        } while (tok != TOKEN_EOF && tok != TOKEN_LEXICAL_ERROR);

        fclose(f);
        return tok == TOKEN_LEXICAL_ERROR ? 1 : 0;
    }

    int parse_errors = 0;
    ASTNode *ast = clara_parse_file(filepath, &parse_errors);

    if (ast == NULL || parse_errors > 0)
    {
        fprintf(stderr, "\n[CLARA] Compilation failed with %d syntax error(s).\n", parse_errors);
        return 1;
    }

    if (show_ast)
    {
        printf("\n=== Abstract Syntax Tree ===\n");
        ast_print(ast, 0);
        printf("============================\n\n");
    }

    /* Semantic Analysis */
    SemanticContext *semantic_ctx = semantic_create();
    if (semantic_ctx == NULL)
    {
        fprintf(stderr, "Error: failed to initialize semantic analyzer.\n");
        ast_free(ast);
        return 1;
    }

    int semantic_result = semantic_analyze(semantic_ctx, ast);
    int semantic_errors = semantic_error_count(semantic_ctx);

    if (semantic_result != 0 || semantic_errors > 0)
    {
        fprintf(stderr, "\n[CLARA] Compilation failed with %d semantic error(s).\n", semantic_errors);
        semantic_destroy(semantic_ctx);
        ast_free(ast);
        return 1;
    }

    if (!check_only)
    {
        printf("[CLARA] Compilation successful: '%s' is structurally and semantically valid.\n", filepath);
        if (semantic_ctx->symbols != NULL)
        {
            printf("[CLARA] Registered %zu symbol(s) in scope.\n", symbol_table_size(semantic_ctx->symbols));
        }
    }

    semantic_destroy(semantic_ctx);
    ast_free(ast);
    return 0;
}
