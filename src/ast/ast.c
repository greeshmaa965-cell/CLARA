#include "ast/ast.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char *ast_duplicate_string(const char *text)
{
    char *copy;

    if (text == NULL)
    {
        return NULL;
    }

    copy = malloc(strlen(text) + 1);

    if (copy == NULL)
    {
        return NULL;
    }

    strcpy(copy, text);
    return copy;
}

static int ast_reserve_children(ASTNode *node, size_t required_capacity)
{
    ASTNode **new_children;
    size_t new_capacity;

    if (node == NULL)
    {
        return 0;
    }

    if (node->child_capacity >= required_capacity)
    {
        return 1;
    }

    new_capacity = node->child_capacity == 0
        ? 4
        : node->child_capacity * 2;

    while (new_capacity < required_capacity)
    {
        new_capacity *= 2;
    }

    new_children = realloc(
        node->children,
        new_capacity * sizeof(ASTNode *)
    );

    if (new_children == NULL)
    {
        return 0;
    }

    node->children = new_children;
    node->child_capacity = new_capacity;

    return 1;
}

ASTNode *ast_create_node(ASTNodeType type)
{
    ASTNode *node;

    node = calloc(1, sizeof(ASTNode));

    if (node == NULL)
    {
        return NULL;
    }

    node->type = type;
    return node;
}

ASTNode *ast_create_named_node(ASTNodeType type, const char *name)
{
    ASTNode *node;

    node = ast_create_node(type);

    if (node == NULL)
    {
        return NULL;
    }

    node->name = ast_duplicate_string(name);

    if (name != NULL && node->name == NULL)
    {
        ast_free(node);
        return NULL;
    }

    return node;
}

ASTNode *ast_create_number_node(ASTNodeType type, long number)
{
    ASTNode *node;

    node = ast_create_node(type);

    if (node == NULL)
    {
        return NULL;
    }

    node->number = number;
    return node;
}

ASTNode *ast_create_quantity_node(
    ASTNodeType type,
    long number,
    const char *unit
)
{
    ASTNode *node;

    node = ast_create_number_node(type, number);

    if (node == NULL)
    {
        return NULL;
    }

    node->unit = ast_duplicate_string(unit);

    if (unit != NULL && node->unit == NULL)
    {
        ast_free(node);
        return NULL;
    }

    return node;
}

void ast_add_child(ASTNode *parent, ASTNode *child)
{
    if (parent == NULL || child == NULL)
    {
        return;
    }

    if (!ast_reserve_children(parent, parent->child_count + 1))
    {
        return;
    }

    parent->children[parent->child_count] = child;
    parent->child_count++;
}

void ast_free(ASTNode *node)
{
    size_t i;

    if (node == NULL)
    {
        return;
    }

    for (i = 0; i < node->child_count; i++)
    {
        ast_free(node->children[i]);
    }

    free(node->children);
    free(node->name);
    free(node->value);
    free(node->unit);
    free(node);
}

const char *ast_node_type_name(ASTNodeType type)
{
    switch (type)
    {
        case AST_PROGRAM:
            return "PROGRAM";

        case AST_CLOUD:
            return "CLOUD";

        case AST_SERVER:
            return "SERVER";

        case AST_DATABASE:
            return "DATABASE";

        case AST_REGION:
            return "REGION";

        case AST_CPU:
            return "CPU";

        case AST_MEMORY:
            return "MEMORY";

        case AST_STORAGE:
            return "STORAGE";

        default:
            return "UNKNOWN";
    }
}

void ast_print(const ASTNode *node, int indentation)
{
    int i;
    size_t j;

    if (node == NULL)
    {
        return;
    }

    for (i = 0; i < indentation; i++)
    {
        printf("  ");
    }

    printf("%s", ast_node_type_name(node->type));

    if (node->name != NULL)
    {
        printf(" name=%s", node->name);
    }

    if (node->value != NULL)
    {
        printf(" value=%s", node->value);
    }

    if (node->type == AST_CPU ||
        node->type == AST_MEMORY ||
        node->type == AST_STORAGE)
    {
        printf(" number=%ld", node->number);

        if (node->unit != NULL)
        {
            printf(" unit=%s", node->unit);
        }
    }

    printf("\n");

    for (j = 0; j < node->child_count; j++)
    {
        ast_print(node->children[j], indentation + 1);
    }
}