from enumeration.device_monitor import USBMonitor


def main():

    ## this the start of the detection service .

    monitor = USBMonitor()

    monitor.start()


if __name__ == "__main__":
    main()
