#ifndef CLARA_SEMANTIC_H
#define CLARA_SEMANTIC_H

#include "ast/ast.h"
#include "semantic/symbol_table.h"

typedef struct SemanticContext
{
    SymbolTable *symbols;

    int error_count;
} SemanticContext;

SemanticContext *semantic_create(void);

void semantic_destroy(SemanticContext *context);

int semantic_analyze(
    SemanticContext *context,
    const ASTNode *root
);

int semantic_error_count(
    const SemanticContext *context
);

#endif