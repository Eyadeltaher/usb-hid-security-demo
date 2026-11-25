CC      := gcc
CFLAGS  := -Wall -Wextra -std=c11 -D_POSIX_C_SOURCE=200809L -g
TARGET  := keylogger_ReverseConnection
SRCS    := keylogger_ReverseConnection.c keyboard_finder.c
OBJS    := $(SRCS:.c=.o)
HDRS    := keyboard_finder.h

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c $(HDRS)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
