#include "semantic/semantic.h"

#include <stdio.h>
#include <stdlib.h>

static void semantic_report_error( //This increments the error count and prints an error message
    SemanticContext *context,
    const char *message,
    const char *name
)
{
    context->error_count++;

    if (name != NULL)
    {
        fprintf(
            stderr,
            "Semantic error: %s '%s'\n",
            message,
            name
        );
    }
    else
    {
        fprintf(
            stderr,
            "Semantic error: %s\n",
            message
        );
    }
}
//create symbols.
static int is_declaration_node(ASTNodeType type)
{
    return type == AST_CLOUD ||
           type == AST_SERVER ||
           type == AST_DATABASE;
}

static SymbolKind symbol_kind_from_ast(ASTNodeType type)
{
    switch (type)
    {
        case AST_CLOUD:
            return SYMBOL_CLOUD;

        case AST_SERVER:
            return SYMBOL_SERVER;

        case AST_DATABASE:
            return SYMBOL_DATABASE;

        default:
            return SYMBOL_CLOUD;
    }
}

static void analyze_node(//walks through every AST node.
    SemanticContext *context,
    const ASTNode *node,
    ASTNodeType parent_type
)
{
    size_t index;

    if (node == NULL)
    {
        return;
    }

    if (is_declaration_node(node->type))
    {
        if (node->name == NULL || node->name[0] == '\0')
        {
            semantic_report_error(
                context,
                "declaration has no name",
                NULL
            );
        }
        else if (!symbol_table_insert(
                     context->symbols,
                     node->name,
                     symbol_kind_from_ast(node->type)))
        {
            semantic_report_error(
                context,
                "duplicate declaration",
                node->name
            );
        }
    }

    if (node->type == AST_SERVER &&
        parent_type != AST_CLOUD)
    {
        semantic_report_error(
            context,
            "server must be declared inside a cloud",
            node->name
        );
    }

    if (node->type == AST_DATABASE &&
        parent_type != AST_CLOUD)
    {
        semantic_report_error(
            context,
            "database must be declared inside a cloud",
            node->name
        );
    }

    if ((node->type == AST_CPU ||
         node->type == AST_MEMORY ||
         node->type == AST_STORAGE) &&
        node->number <= 0)
    {
        semantic_report_error(
            context,
            "resource value must be greater than zero",
            node->name
        );
    }

    if ((node->type == AST_MEMORY ||
         node->type == AST_STORAGE) &&
        (node->unit == NULL || node->unit[0] == '\0'))
    {
        semantic_report_error(
            context,
            "resource quantity requires a unit",
            node->name
        );
    }

    for (index = 0; index < node->child_count; index++)
    {
        analyze_node(
            context,
            node->children[index],
            node->type
        );
    }
}

SemanticContext *semantic_create(void)
{
    SemanticContext *context;

    context = malloc(sizeof(SemanticContext));

    if (context == NULL)
    {
        return NULL;
    }

    context->symbols = symbol_table_create(32);
    context->error_count = 0;

    if (context->symbols == NULL)
    {
        free(context);
        return NULL;
    }

    return context;
}

void semantic_destroy(SemanticContext *context)
{
    if (context == NULL)
    {
        return;
    }

    symbol_table_destroy(context->symbols);
    free(context);
}

int semantic_analyze(
    SemanticContext *context,
    const ASTNode *root
)
{
    if (context == NULL || root == NULL)
    {
        return -1;
    }

    context->error_count = 0;

    symbol_table_destroy(context->symbols);
    context->symbols = symbol_table_create(32);

    if (context->symbols == NULL)
    {
        return -1;
    }

    analyze_node(context, root, AST_PROGRAM);

    return context->error_count == 0 ? 0 : -1;
}

int semantic_error_count(
    const SemanticContext *context
)
{
    if (context == NULL)
    {
        return -1;
    }

    return context->error_count;
}