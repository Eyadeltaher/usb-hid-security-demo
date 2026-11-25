#include <ctype.h>
#include <dirent.h>
#include <fcntl.h>
#include <linux/input.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#define BITS_PER_LONG (sizeof(unsigned long) * 8)
#define NBITS(x)      ((((x) - 1) / BITS_PER_LONG) + 1)
#define OFF(x)        ((x) % BITS_PER_LONG)
#define LONG(x)       ((x) / BITS_PER_LONG)
#define test_bit(bit, array) ((array[LONG(bit)] >> OFF(bit)) & 1UL)

static bool is_keyboard(int fd) {
    unsigned long ev_bits[NBITS(EV_CNT)] = {0};
    unsigned long key_bits[NBITS(KEY_CNT)] = {0};


    if (ioctl(fd, EVIOCGBIT(0, sizeof(ev_bits)), ev_bits) < 0) {
        return false;
    }


    if (!test_bit(EV_KEY, ev_bits)) {
        return false;
    }

    if (ioctl(fd, EVIOCGBIT(EV_KEY, sizeof(key_bits)), key_bits) < 0) {
        return false;
    }


    for (int key = KEY_Q; key <= KEY_P; key++) {
        if (!test_bit(key, key_bits)) {
            return false;
        }
    }

    return test_bit(KEY_ENTER, key_bits);
}


char *find_keyboard_path(void) {
    DIR *dir = opendir("/dev/input");
    if (!dir) {
        return NULL;
    }

    struct dirent *entry;
    char path[512];
    char *result = NULL;

    while ((entry = readdir(dir)) != NULL) {
        
        if (strncmp(entry->d_name, "event", 5) != 0 ||
            !isdigit((unsigned char)entry->d_name[5])) {
            continue;
        }

        snprintf(path, sizeof(path), "/dev/input/%s", entry->d_name);

        int fd = open(path, O_RDONLY | O_NONBLOCK);
        if (fd < 0) {
            continue; 
        }

        if (is_keyboard(fd)) {
            result = strdup(path);
            close(fd);
            break;
        }

        close(fd);
    }

    closedir(dir);
    return result;
}
