#include "parser/parser.h"
#include "tokens.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern FILE *yyin;
extern int yylineno;
extern char *yytext;
int yylex(void);
void clara_lexer_reset(void);

struct Parser
{
    FILE *input;
    TokenType current_token;
    char current_text[256];
    int current_line;
    int error_count;
};

static void parser_report_error(Parser *parser, const char *message)
{
    parser->error_count++;
    fprintf(
        stderr,
        "Syntax error: line %d: %s (near '%s')\n",
        parser->current_line,
        message,
        parser->current_text
    );
}

static void parser_advance(Parser *parser)
{
    parser->current_token = (TokenType)yylex();
    parser->current_line = yylineno;

    if (yytext != NULL)
    {
        strncpy(parser->current_text, yytext, sizeof(parser->current_text) - 1);
        parser->current_text[sizeof(parser->current_text) - 1] = '\0';
    }
    else
    {
        parser->current_text[0] = '\0';
    }

    if (parser->current_token == TOKEN_LEXICAL_ERROR)
    {
        parser->error_count++;
    }
}

static int parser_match(Parser *parser, TokenType expected)
{
    if (parser->current_token == expected)
    {
        parser_advance(parser);
        return 1;
    }

    char message[128];
    snprintf(
        message,
        sizeof(message),
        "expected '%s', got '%s'",
        token_type_name(expected),
        token_type_name(parser->current_token)
    );
    parser_report_error(parser, message);
    return 0;
}

static ASTNode *parse_server(Parser *parser)
{
    char server_name[128];

    if (!parser_match(parser, TOKEN_SERVER))
    {
        return NULL;
    }

    if (parser->current_token != TOKEN_IDENTIFIER)
    {
        parser_report_error(parser, "expected server identifier");
        return NULL;
    }

    strncpy(server_name, parser->current_text, sizeof(server_name) - 1);
    server_name[sizeof(server_name) - 1] = '\0';
    parser_advance(parser);

    if (!parser_match(parser, TOKEN_LBRACE))
    {
        return NULL;
    }

    ASTNode *server = ast_create_named_node(AST_SERVER, server_name);
    if (server == NULL)
    {
        return NULL;
    }

    while (parser->current_token != TOKEN_RBRACE &&
           parser->current_token != TOKEN_EOF)
    {
        if (parser->current_token == TOKEN_CPU)
        {
            parser_advance(parser);
            if (parser->current_token == TOKEN_NUMBER)
            {
                long cpu = strtol(parser->current_text, NULL, 10);
                ast_add_child(server, ast_create_number_node(AST_CPU, cpu));
                parser_advance(parser);
            }
            else
            {
                parser_report_error(parser, "expected integer for CPU count");
            }
        }
        else if (parser->current_token == TOKEN_MEMORY)
        {
            parser_advance(parser);
            if (parser->current_token == TOKEN_NUMBER)
            {
                long mem = strtol(parser->current_text, NULL, 10);
                parser_advance(parser);

                const char *unit = "";
                char unit_buf[32] = "";
                if (parser->current_token == TOKEN_UNIT)
                {
                    strncpy(unit_buf, parser->current_text, sizeof(unit_buf) - 1);
                    unit = unit_buf;
                    parser_advance(parser);
                }

                ast_add_child(server, ast_create_quantity_node(AST_MEMORY, mem, unit));
            }
            else
            {
                parser_report_error(parser, "expected quantity for MEMORY");
            }
        }
        else if (parser->current_token == TOKEN_STORAGE)
        {
            parser_advance(parser);
            if (parser->current_token == TOKEN_NUMBER)
            {
                long storage = strtol(parser->current_text, NULL, 10);
                parser_advance(parser);

                const char *unit = "";
                char unit_buf[32] = "";
                if (parser->current_token == TOKEN_UNIT)
                {
                    strncpy(unit_buf, parser->current_text, sizeof(unit_buf) - 1);
                    unit = unit_buf;
                    parser_advance(parser);
                }

                ast_add_child(server, ast_create_quantity_node(AST_STORAGE, storage, unit));
            }
            else
            {
                parser_report_error(parser, "expected quantity for STORAGE");
            }
        }
        else
        {
            parser_report_error(parser, "unexpected token in SERVER definition");
            parser_advance(parser);
        }
    }

    if (!parser_match(parser, TOKEN_RBRACE))
    {
        ast_free(server);
        return NULL;
    }

    return server;
}

static ASTNode *parse_database(Parser *parser)
{
    char db_name[128];

    if (!parser_match(parser, TOKEN_DATABASE))
    {
        return NULL;
    }

    if (parser->current_token != TOKEN_IDENTIFIER)
    {
        parser_report_error(parser, "expected database identifier");
        return NULL;
    }

    strncpy(db_name, parser->current_text, sizeof(db_name) - 1);
    db_name[sizeof(db_name) - 1] = '\0';
    parser_advance(parser);

    if (!parser_match(parser, TOKEN_LBRACE))
    {
        return NULL;
    }

    ASTNode *db = ast_create_named_node(AST_DATABASE, db_name);
    if (db == NULL)
    {
        return NULL;
    }

    while (parser->current_token != TOKEN_RBRACE &&
           parser->current_token != TOKEN_EOF)
    {
        if (parser->current_token == TOKEN_STORAGE)
        {
            parser_advance(parser);
            if (parser->current_token == TOKEN_NUMBER)
            {
                long storage = strtol(parser->current_text, NULL, 10);
                parser_advance(parser);

                const char *unit = "";
                char unit_buf[32] = "";
                if (parser->current_token == TOKEN_UNIT)
                {
                    strncpy(unit_buf, parser->current_text, sizeof(unit_buf) - 1);
                    unit = unit_buf;
                    parser_advance(parser);
                }

                ast_add_child(db, ast_create_quantity_node(AST_STORAGE, storage, unit));
            }
            else
            {
                parser_report_error(parser, "expected quantity for STORAGE");
            }
        }
        else if (parser->current_token == TOKEN_CPU)
        {
            parser_advance(parser);
            if (parser->current_token == TOKEN_NUMBER)
            {
                long cpu = strtol(parser->current_text, NULL, 10);
                ast_add_child(db, ast_create_number_node(AST_CPU, cpu));
                parser_advance(parser);
            }
            else
            {
                parser_report_error(parser, "expected integer for CPU count");
            }
        }
        else if (parser->current_token == TOKEN_MEMORY)
        {
            parser_advance(parser);
            if (parser->current_token == TOKEN_NUMBER)
            {
                long mem = strtol(parser->current_text, NULL, 10);
                parser_advance(parser);

                const char *unit = "";
                char unit_buf[32] = "";
                if (parser->current_token == TOKEN_UNIT)
                {
                    strncpy(unit_buf, parser->current_text, sizeof(unit_buf) - 1);
                    unit = unit_buf;
                    parser_advance(parser);
                }

                ast_add_child(db, ast_create_quantity_node(AST_MEMORY, mem, unit));
            }
            else
            {
                parser_report_error(parser, "expected quantity for MEMORY");
            }
        }
        else
        {
            parser_report_error(parser, "unexpected token in DATABASE definition");
            parser_advance(parser);
        }
    }

    if (!parser_match(parser, TOKEN_RBRACE))
    {
        ast_free(db);
        return NULL;
    }

    return db;
}

static ASTNode *parse_cloud(Parser *parser)
{
    char cloud_name[128];

    if (!parser_match(parser, TOKEN_CLOUD))
    {
        return NULL;
    }

    if (parser->current_token != TOKEN_IDENTIFIER)
    {
        parser_report_error(parser, "expected cloud provider identifier (e.g. AWS, Azure, GCP)");
        return NULL;
    }

    strncpy(cloud_name, parser->current_text, sizeof(cloud_name) - 1);
    cloud_name[sizeof(cloud_name) - 1] = '\0';
    parser_advance(parser);

    if (!parser_match(parser, TOKEN_LBRACE))
    {
        return NULL;
    }

    ASTNode *cloud = ast_create_named_node(AST_CLOUD, cloud_name);
    if (cloud == NULL)
    {
        return NULL;
    }

    while (parser->current_token != TOKEN_RBRACE &&
           parser->current_token != TOKEN_EOF)
    {
        if (parser->current_token == TOKEN_REGION)
        {
            parser_advance(parser);
            if (parser->current_token == TOKEN_IDENTIFIER)
            {
                ast_add_child(cloud, ast_create_named_node(AST_REGION, parser->current_text));
                parser_advance(parser);
            }
            else
            {
                parser_report_error(parser, "expected region identifier");
            }
        }
        else if (parser->current_token == TOKEN_SERVER)
        {
            ASTNode *server = parse_server(parser);
            if (server != NULL)
            {
                ast_add_child(cloud, server);
            }
        }
        else if (parser->current_token == TOKEN_DATABASE)
        {
            ASTNode *db = parse_database(parser);
            if (db != NULL)
            {
                ast_add_child(cloud, db);
            }
        }
        else
        {
            parser_report_error(parser, "unexpected token in CLOUD definition");
            parser_advance(parser);
        }
    }

    if (!parser_match(parser, TOKEN_RBRACE))
    {
        ast_free(cloud);
        return NULL;
    }

    return cloud;
}

Parser *parser_create(FILE *input)
{
    Parser *parser = (Parser *)malloc(sizeof(Parser));
    if (parser == NULL)
    {
        return NULL;
    }

    parser->input = input;
    parser->error_count = 0;
    parser->current_line = 1;
    parser->current_text[0] = '\0';

    clara_lexer_reset();
    yyin = input;

    /* Prime the first token */
    parser_advance(parser);

    return parser;
}

void parser_destroy(Parser *parser)
{
    if (parser != NULL)
    {
        free(parser);
    }
}

ASTNode *parser_parse(Parser *parser)
{
    if (parser == NULL)
    {
        return NULL;
    }

    ASTNode *program = ast_create_node(AST_PROGRAM);
    if (program == NULL)
    {
        return NULL;
    }

    while (parser->current_token == TOKEN_CLOUD)
    {
        ASTNode *cloud = parse_cloud(parser);
        if (cloud != NULL)
        {
            ast_add_child(program, cloud);
        }
    }

    if (parser->current_token != TOKEN_EOF)
    {
        parser_report_error(parser, "unexpected token outside CLOUD block");
    }

    if (parser->error_count > 0)
    {
        ast_free(program);
        return NULL;
    }

    return program;
}

int parser_error_count(const Parser *parser)
{
    return parser != NULL ? parser->error_count : -1;
}

ASTNode *clara_parse_file(const char *filepath, int *error_count)
{
    FILE *file = fopen(filepath, "r");
    if (file == NULL)
    {
        fprintf(stderr, "Error: could not open file '%s'\n", filepath);
        if (error_count != NULL)
        {
            *error_count = 1;
        }
        return NULL;
    }

    Parser *parser = parser_create(file);
    if (parser == NULL)
    {
        fclose(file);
        if (error_count != NULL)
        {
            *error_count = 1;
        }
        return NULL;
    }

    ASTNode *ast = parser_parse(parser);
    int errors = parser_error_count(parser);

    if (error_count != NULL)
    {
        *error_count = errors;
    }

    parser_destroy(parser);
    fclose(file);

    return ast;
}
