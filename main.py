import datetime
import time

if __name__ == '__main__':
    print("--- ROUTE-ENGINE: ---")
    start_time = time.time()
    main()
    end_time = int(time.time() - start_time)
    end_time = str(datetime.timedelta(seconds=end_time))
    print("--- END: %s ---" % end_time)
