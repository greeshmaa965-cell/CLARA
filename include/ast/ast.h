#ifndef CLARA_AST_H
#define CLARA_AST_H

#include <stddef.h>

typedef enum
{
    AST_PROGRAM,
    AST_CLOUD,
    AST_SERVER,
    AST_DATABASE,
    AST_REGION,
    AST_CPU,
    AST_MEMORY,
    AST_STORAGE
} ASTNodeType;

typedef struct ASTNode ASTNode;

struct ASTNode
{
    ASTNodeType type;

    char *name;
    char *value;
    char *unit;

    long number;

    ASTNode **children;
    size_t child_count;
    size_t child_capacity;
};

ASTNode *ast_create_node(ASTNodeType type);

ASTNode *ast_create_named_node(ASTNodeType type, const char *name);

ASTNode *ast_create_number_node(ASTNodeType type, long number);

ASTNode *ast_create_quantity_node(
    ASTNodeType type,
    long number,
    const char *unit
);

void ast_add_child(ASTNode *parent, ASTNode *child);

void ast_free(ASTNode *node);

const char *ast_node_type_name(ASTNodeType type);

void ast_print(const ASTNode *node, int indentation);

#endif