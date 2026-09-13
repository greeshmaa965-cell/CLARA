#include "ast/ast.h"
#include "semantic/semantic.h"

#include <stdio.h>

static ASTNode *create_valid_program(void)
{
    ASTNode *program;
    ASTNode *cloud;
    ASTNode *server;
    ASTNode *cpu;
    ASTNode *memory;

    program = ast_create_node(AST_PROGRAM);

    cloud = ast_create_named_node(AST_CLOUD, "aws");
    ast_add_child(program, cloud);

    server = ast_create_named_node(AST_SERVER, "web");
    ast_add_child(cloud, server);

    cpu = ast_create_number_node(AST_CPU, 4);
    ast_add_child(server, cpu);

    memory = ast_create_quantity_node(AST_MEMORY, 16, "GB");
    ast_add_child(server, memory);

    return program;
}

static ASTNode *create_invalid_program(void)
{
    ASTNode *program;
    ASTNode *cloud1;
    ASTNode *cloud2;
    ASTNode *server;
    ASTNode *memory;

    program = ast_create_node(AST_PROGRAM);

    cloud1 = ast_create_named_node(AST_CLOUD, "aws");
    ast_add_child(program, cloud1);

    cloud2 = ast_create_named_node(AST_CLOUD, "aws");
    ast_add_child(program, cloud2);

    server = ast_create_named_node(AST_SERVER, "web");
    ast_add_child(program, server);

    memory = ast_create_quantity_node(AST_MEMORY, 0, "");
    ast_add_child(cloud1, memory);

    return program;
}

static int test_valid_program(void)
{
    ASTNode *program;
    SemanticContext *context;
    int result;

    program = create_valid_program();
    context = semantic_create();

    if (program == NULL || context == NULL)
    {
        printf("Failed to create valid-program test objects.\n");

        ast_free(program);
        semantic_destroy(context);

        return 1;
    }

    result = semantic_analyze(context, program);

    printf(
        "Valid program result: %s\n",
        result == 0 ? "passed" : "failed"
    );

    printf(
        "Valid program errors: %d\n",
        semantic_error_count(context)
    );

    ast_free(program);
    semantic_destroy(context);

    return result == 0 ? 0 : 1;
}

static int test_invalid_program(void)
{
    ASTNode *program;
    SemanticContext *context;
    int result;

    program = create_invalid_program();
    context = semantic_create();

    if (program == NULL || context == NULL)
    {
        printf("Failed to create invalid-program test objects.\n");

        ast_free(program);
        semantic_destroy(context);

        return 1;
    }

    result = semantic_analyze(context, program);

    printf(
        "Invalid program result: %s\n",
        result != 0 ? "passed" : "failed"
    );

    printf(
        "Invalid program errors: %d\n",
        semantic_error_count(context)
    );

    ast_free(program);
    semantic_destroy(context);

    return result != 0 ? 0 : 1;
}

int main(void)
{
    if (test_valid_program() != 0)
    {
        return 1;
    }

    if (test_invalid_program() != 0)
    {
        return 1;
    }

    printf("Semantic analyzer tests passed.\n");

    return 0;
}