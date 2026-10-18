#include "parser/parser.h"
#include "ast/ast.h"

#include <stdio.h>
#include <assert.h>

static int test_parse_valid(void)
{
    int error_count = 0;
    ASTNode *ast = clara_parse_file("tests/lexer/valid.clara", &error_count);

    if (ast == NULL || error_count > 0)
    {
        printf("FAILED: valid.clara failed to parse (errors: %d)\n", error_count);
        return 1;
    }

    /* Verify AST structure */
    assert(ast->type == AST_PROGRAM);
    assert(ast->child_count == 1);

    ASTNode *cloud = ast->children[0];
    assert(cloud->type == AST_CLOUD);
    assert(cloud->name != NULL);

    printf("PASSED: test_parse_valid (AST generated successfully)\n");
    ast_print(ast, 0);

    ast_free(ast);
    return 0;
}

static int test_parse_comments(void)
{
    int error_count = 0;
    ASTNode *ast = clara_parse_file("tests/lexer/comments.clara", &error_count);

    if (ast == NULL || error_count > 0)
    {
        printf("FAILED: comments.clara failed to parse\n");
        return 1;
    }

    printf("PASSED: test_parse_comments\n");
    ast_free(ast);
    return 0;
}

static int test_parse_edge_cases(void)
{
    int error_count = 0;
    ASTNode *ast = clara_parse_file("tests/lexer/edge_cases.clara", &error_count);

    if (ast == NULL || error_count > 0)
    {
        printf("FAILED: edge_cases.clara failed to parse\n");
        return 1;
    }

    printf("PASSED: test_parse_edge_cases\n");
    ast_free(ast);
    return 0;
}

static int test_parse_invalid(void)
{
    int error_count = 0;
    ASTNode *ast = clara_parse_file("tests/lexer/invalid.clara", &error_count);

    if (ast != NULL || error_count == 0)
    {
        printf("FAILED: invalid.clara should have failed parsing\n");
        if (ast) ast_free(ast);
        return 1;
    }

    printf("PASSED: test_parse_invalid (correctly rejected invalid syntax with %d errors)\n", error_count);
    return 0;
}

int main(void)
{
    int failures = 0;

    printf("--- Running CLARA Parser Tests ---\n");

    failures += test_parse_valid();
    failures += test_parse_comments();
    failures += test_parse_edge_cases();
    failures += test_parse_invalid();

    if (failures == 0)
    {
        printf("\nAll parser tests PASSED successfully!\n");
        return 0;
    }
    else
    {
        printf("\nParser tests FAILED with %d failure(s).\n", failures);
        return 1;
    }
}
