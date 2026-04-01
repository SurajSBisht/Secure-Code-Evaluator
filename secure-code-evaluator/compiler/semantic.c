#include <stdio.h>
#include <string.h>
#include <ctype.h>

#define MAX_VARS 100

char declaredVars[MAX_VARS][50];
int varCount = 0;

int isDeclared(char var[]) {
    for (int i = 0; i < varCount; i++) {
        if (strcmp(declaredVars[i], var) == 0)
            return 1;
    }
    return 0;
}

void declareVar(char var[]) {
    strcpy(declaredVars[varCount], var);
    varCount++;
}

int isKeyword(char word[]) {
    return strcmp(word, "int") == 0 || strcmp(word, "print") == 0 ||
           strcmp(word, "if") == 0 || strcmp(word, "else") == 0 ||
           strcmp(word, "while") == 0;
}

int main() {
    FILE *fp;
    char line[200];
    int lineNo = 1;
    int semanticError = 0;

    fp = fopen("input.txt", "r");

    if (fp == NULL) {
        printf("Error opening file!\n");
        return 1;
    }

    printf("Semantic Analysis Output:\n\n");

    while (fgets(line, sizeof(line), fp)) {
        char word[50];
        int i = 0, j = 0;

        // Check for declaration like: int a = 5;
        if (strncmp(line, "int ", 4) == 0) {
            i = 4;
            j = 0;

            while (isalnum(line[i]) || line[i] == '_') {
                word[j++] = line[i++];
            }
            word[j] = '\0';

            if (isDeclared(word)) {
                printf("Semantic Error at line %d: Duplicate declaration of variable '%s'\n", lineNo, word);
                semanticError = 1;
            } else {
                declareVar(word);
            }
        }

        // Check for usage of undeclared variable
        for (i = 0; line[i] != '\0'; i++) {
            if (isalpha(line[i]) || line[i] == '_') {
                j = 0;
                while (isalnum(line[i]) || line[i] == '_') {
                    word[j++] = line[i++];
                }
                word[j] = '\0';

                if (!isKeyword(word) && !isDeclared(word)) {
                    printf("Semantic Error at line %d: Variable '%s' used before declaration\n", lineNo, word);
                    semanticError = 1;
                }
            }
        }

        lineNo++;
    }

    fclose(fp);

    if (!semanticError) {
        printf("No semantic errors found.\n");
    }

    return 0;
}
