
#include <stdio.h>
#include <ctype.h>
#include <string.h>

int isKeyword(char str[]) {
    char keywords[][10] = {"int", "if", "else", "while", "print", "return"};
    int n = 6;

    for (int i = 0; i < n; i++) {
        if (strcmp(str, keywords[i]) == 0)
            return 1;
    }
    return 0;
}

int main() {
    FILE *fp;
    char ch, buffer[100];
    int i = 0;

    fp = fopen("input.txt", "r");

    if (fp == NULL) {
        printf("Error opening file!\n");
        return 1;
    }

    printf("Lexical Analysis Output:\n\n");

    while ((ch = fgetc(fp)) != EOF) {
        // Ignore spaces and new lines
        if (isspace(ch)) {
            continue;
        }

        // Identifier or keyword
        if (isalpha(ch) || ch == '_') {
            buffer[i++] = ch;
            while ((ch = fgetc(fp)) != EOF && (isalnum(ch) || ch == '_')) {
                buffer[i++] = ch;
            }
            buffer[i] = '\0';
            i = 0;

            if (isKeyword(buffer))
                printf("Keyword: %s\n", buffer);
            else
                printf("Identifier: %s\n", buffer);

            if (ch != EOF)
                ungetc(ch, fp);
        }

        // Number
        else if (isdigit(ch)) {
            buffer[i++] = ch;
            while ((ch = fgetc(fp)) != EOF && isdigit(ch)) {
                buffer[i++] = ch;
            }
            buffer[i] = '\0';
            i = 0;

            printf("Number: %s\n", buffer);

            if (ch != EOF)
                ungetc(ch, fp);
        }

        // Operators
        else if (ch == '+' || ch == '-' || ch == '*' || ch == '/' || ch == '=' || ch == '<' || ch == '>') {
            printf("Operator: %c\n", ch);
        }

        // Delimiters
        else if (ch == ';' || ch == ',' || ch == '(' || ch == ')' || ch == '{' || ch == '}') {
            printf("Delimiter: %c\n", ch);
        }

        // Unknown
        else {
            printf("Unknown Symbol: %c\n", ch);
        }
    }

    fclose(fp);
    return 0;
}