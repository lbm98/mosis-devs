def my_log(string):
    with open('log.txt', 'a') as fh:
        fh.write(string + '\n')
