#include "ir/ir.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

static double normalize_to_gb(long number, const char *unit)
{
    if (unit == NULL || unit[0] == '\0')
    {
        return (double)number;
    }

    if (strcmp(unit, "MB") == 0)
    {
        return (double)number / 1024.0;
    }
    else if (strcmp(unit, "TB") == 0)
    {
        return (double)number * 1024.0;
    }

    /* Default GB */
    return (double)number;
}

static void str_to_lower(char *dest, const char *src, size_t max_len)
{
    size_t i = 0;
    while (src[i] != '\0' && i < max_len - 1)
    {
        dest[i] = (char)tolower((unsigned char)src[i]);
        i++;
    }
    dest[i] = '\0';
}

CLARA_IR *ir_build_from_ast(const ASTNode *ast)
{
    if (ast == NULL || ast->type != AST_PROGRAM)
    {
        return NULL;
    }

    CLARA_IR *ir = (CLARA_IR *)calloc(1, sizeof(CLARA_IR));
    if (ir == NULL)
    {
        return NULL;
    }

    strncpy(ir->region, "default", sizeof(ir->region) - 1);

    size_t i, j, k;
    for (i = 0; i < ast->child_count; i++)
    {
        const ASTNode *cloud = ast->children[i];
        if (cloud->type != AST_CLOUD)
        {
            continue;
        }

        if (cloud->name != NULL)
        {
            str_to_lower(ir->provider, cloud->name, sizeof(ir->provider));
        }

        for (j = 0; j < cloud->child_count; j++)
        {
            const ASTNode *child = cloud->children[j];
            if (child->type == AST_REGION)
            {
                if (child->name != NULL)
                {
                    strncpy(ir->region, child->name, sizeof(ir->region) - 1);
                    ir->region[sizeof(ir->region) - 1] = '\0';
                }
            }
            else if (child->type == AST_SERVER)
            {
                if (ir->server_count >= ir->server_capacity)
                {
                    size_t new_cap = ir->server_capacity == 0 ? 4 : ir->server_capacity * 2;
                    IRServer *new_servers = (IRServer *)realloc(ir->servers, new_cap * sizeof(IRServer));
                    if (new_servers == NULL) continue;
                    ir->servers = new_servers;
                    ir->server_capacity = new_cap;
                }

                IRServer *srv = &ir->servers[ir->server_count++];
                memset(srv, 0, sizeof(IRServer));
                if (child->name != NULL)
                {
                    strncpy(srv->name, child->name, sizeof(srv->name) - 1);
                }

                for (k = 0; k < child->child_count; k++)
                {
                    const ASTNode *prop = child->children[k];
                    if (prop->type == AST_CPU)
                    {
                        srv->cpu = (int)prop->number;
                    }
                    else if (prop->type == AST_MEMORY)
                    {
                        srv->memory_gb = normalize_to_gb(prop->number, prop->unit);
                    }
                    else if (prop->type == AST_STORAGE)
                    {
                        srv->storage_gb = normalize_to_gb(prop->number, prop->unit);
                    }
                }
            }
            else if (child->type == AST_DATABASE)
            {
                if (ir->database_count >= ir->database_capacity)
                {
                    size_t new_cap = ir->database_capacity == 0 ? 4 : ir->database_capacity * 2;
                    IRDatabase *new_dbs = (IRDatabase *)realloc(ir->databases, new_cap * sizeof(IRDatabase));
                    if (new_dbs == NULL) continue;
                    ir->databases = new_dbs;
                    ir->database_capacity = new_cap;
                }

                IRDatabase *db = &ir->databases[ir->database_count++];
                memset(db, 0, sizeof(IRDatabase));
                if (child->name != NULL)
                {
                    strncpy(db->name, child->name, sizeof(db->name) - 1);
                }

                for (k = 0; k < child->child_count; k++)
                {
                    const ASTNode *prop = child->children[k];
                    if (prop->type == AST_CPU)
                    {
                        db->cpu = (int)prop->number;
                    }
                    else if (prop->type == AST_MEMORY)
                    {
                        db->memory_gb = normalize_to_gb(prop->number, prop->unit);
                    }
                    else if (prop->type == AST_STORAGE)
                    {
                        db->storage_gb = normalize_to_gb(prop->number, prop->unit);
                    }
                }
            }
        }
    }

    return ir;
}

void ir_destroy(CLARA_IR *ir)
{
    if (ir == NULL)
    {
        return;
    }

    if (ir->servers != NULL)
    {
        free(ir->servers);
    }

    if (ir->databases != NULL)
    {
        free(ir->databases);
    }

    free(ir);
}

char *ir_to_json(const CLARA_IR *ir)
{
    if (ir == NULL)
    {
        return NULL;
    }

    /* Allocate buffer for formatted JSON */
    size_t buf_size = 4096;
    char *json = (char *)malloc(buf_size);
    if (json == NULL)
    {
        return NULL;
    }

    size_t offset = 0;
    offset += snprintf(json + offset, buf_size - offset,
        "{\n"
        "  \"schema_version\": \"1.0\",\n"
        "  \"provider\": \"%s\",\n"
        "  \"region\": \"%s\",\n"
        "  \"resources\": {\n"
        "    \"servers\": [\n",
        ir->provider, ir->region
    );

    size_t i;
    for (i = 0; i < ir->server_count; i++)
    {
        const IRServer *s = &ir->servers[i];
        offset += snprintf(json + offset, buf_size - offset,
            "      {\n"
            "        \"name\": \"%s\",\n"
            "        \"cpu\": %d,\n"
            "        \"memory_gb\": %.2f,\n"
            "        \"storage_gb\": %.2f\n"
            "      }%s\n",
            s->name, s->cpu, s->memory_gb, s->storage_gb,
            (i + 1 < ir->server_count) ? "," : ""
        );
    }

    offset += snprintf(json + offset, buf_size - offset,
        "    ],\n"
        "    \"databases\": [\n"
    );

    for (i = 0; i < ir->database_count; i++)
    {
        const IRDatabase *db = &ir->databases[i];
        offset += snprintf(json + offset, buf_size - offset,
            "      {\n"
            "        \"name\": \"%s\",\n"
            "        \"cpu\": %d,\n"
            "        \"memory_gb\": %.2f,\n"
            "        \"storage_gb\": %.2f\n"
            "      }%s\n",
            db->name, db->cpu, db->memory_gb, db->storage_gb,
            (i + 1 < ir->database_count) ? "," : ""
        );
    }

    offset += snprintf(json + offset, buf_size - offset,
        "    ]\n"
        "  }\n"
        "}\n"
    );

    return json;
}

void ir_print(const CLARA_IR *ir)
{
    if (ir == NULL)
    {
        printf("IR: NULL\n");
        return;
    }

    printf("=== CLARA Intermediate Representation ===\n");
    printf("Provider: %s\n", ir->provider);
    printf("Region:   %s\n", ir->region);
    printf("Servers (%zu):\n", ir->server_count);
    size_t i;
    for (i = 0; i < ir->server_count; i++)
    {
        printf("  - [%s] CPU: %d cores | Memory: %.1f GB | Storage: %.1f GB\n",
            ir->servers[i].name, ir->servers[i].cpu, ir->servers[i].memory_gb, ir->servers[i].storage_gb);
    }
    printf("Databases (%zu):\n", ir->database_count);
    for (i = 0; i < ir->database_count; i++)
    {
        printf("  - [%s] Storage: %.1f GB (CPU: %d, Memory: %.1f GB)\n",
            ir->databases[i].name, ir->databases[i].storage_gb, ir->databases[i].cpu, ir->databases[i].memory_gb);
    }
    printf("=========================================\n");
}
