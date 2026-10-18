#include "parser/parser.h"
#include "ast/ast.h"
#include "semantic/semantic.h"
#include "ir/ir.h"
#include "codegen/codegen.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

int main(void)
{
    printf("--- Running CLARA IR and Codegen Tests ---\n");

    int parse_errors = 0;
    ASTNode *ast = clara_parse_file("tests/lexer/valid.clara", &parse_errors);
    assert(ast != NULL);
    assert(parse_errors == 0);

    SemanticContext *ctx = semantic_create();
    assert(ctx != NULL);
    int sem_result = semantic_analyze(ctx, ast);
    assert(sem_result == 0);

    CLARA_IR *ir = ir_build_from_ast(ast);
    assert(ir != NULL);
    assert(strcmp(ir->provider, "aws") == 0);
    assert(strcmp(ir->region, "ap-south-1") == 0);
    assert(ir->server_count == 1);
    assert(ir->database_count == 1);
    assert(strcmp(ir->servers[0].name, "web_server") == 0);
    assert(ir->servers[0].cpu == 4);
    assert(ir->servers[0].memory_gb == 16.0);
    assert(ir->servers[0].storage_gb == 100.0);
    assert(strcmp(ir->databases[0].name, "main_db") == 0);
    assert(ir->databases[0].storage_gb == 500.0);

    /* Test IR JSON serialization */
    char *json = ir_to_json(ir);
    assert(json != NULL);
    assert(strstr(json, "\"provider\": \"aws\"") != NULL);
    assert(strstr(json, "\"name\": \"web_server\"") != NULL);
    assert(strstr(json, "\"storage_gb\": 500.00") != NULL);
    printf("PASSED: IR JSON serialization\n%s\n", json);
    free(json);

    /* Test Terraform code generation */
    char *tf = codegen_generate_terraform(ir);
    assert(tf != NULL);
    assert(strstr(tf, "provider \"aws\"") != NULL);
    assert(strstr(tf, "resource \"aws_instance\" \"web_server\"") != NULL);
    assert(strstr(tf, "resource \"aws_db_instance\" \"main_db\"") != NULL);
    printf("PASSED: Terraform code generation\n%s\n", tf);
    free(tf);

    ir_destroy(ir);
    semantic_destroy(ctx);
    ast_free(ast);

    printf("All IR and Codegen tests PASSED successfully!\n");
    return 0;
}
