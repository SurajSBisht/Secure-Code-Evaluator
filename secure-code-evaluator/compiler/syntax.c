#include <stdio.h>
#include <string.h>

int checkSemicolon(char line[]) {
    int len = strlen(line);

    // Ignore empty lines and lines with only braces
    if (len <= 1 || strcmp(line, "\n") == 0)
        return 1;

    if (line[0] == '{' || line[0] == '}')
        return 1;

    // Remove newline before checking
    if (line[len - 1] == '\n') {
        line[len - 1] = '\0';
        len--;
    }

    // Check if line ends with semicolon or brace
    if (line[len - 1] == ';' || line[len - 1] == '{' || line[len - 1] == '}')
        return 1;

    return 0;
}

int main() {
    FILE *fp;
    char line[200];
    int lineNo = 1;
    int openParen = 0, closeParen = 0;
    int openBrace = 0, closeBrace = 0;
    int syntaxError = 0;

    fp = fopen("input.txt", "r");

    if (fp == NULL) {
        printf("Error opening file!\n");
        return 1;
    }

    printf("Syntax Analysis Output:\n\n");

    while (fgets(line, sizeof(line), fp)) {
        // Check semicolon
        if (!checkSemicolon(line)) {
            printf("Syntax Error at line %d: Missing semicolon\n", lineNo);
            syntaxError = 1;
        }

        // Count brackets and braces
        for (int i = 0; line[i] != '\0'; i++) {
            if (line[i] == '(') openParen++;
            if (line[i] == ')') closeParen++;
            if (line[i] == '{') openBrace++;
            if (line[i] == '}') closeBrace++;
        }

        lineNo++;
    }

    fclose(fp);

    if (openParen != closeParen) {
        printf("Syntax Error: Unmatched parentheses\n");
        syntaxError = 1;
    }

    if (openBrace != closeBrace) {
        printf("Syntax Error: Unmatched curly braces\n");
        syntaxError = 1;
    }

    if (!syntaxError) {
        printf("No syntax errors found.\n");
    }

    return 0;
}
