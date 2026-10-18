#ifndef CLARA_CODEGEN_H
#define CLARA_CODEGEN_H

#include "ir/ir.h"

/* Generates production-ready Terraform HCL configuration from the CLARA IR */
char *codegen_generate_terraform(const CLARA_IR *ir);

#endif
