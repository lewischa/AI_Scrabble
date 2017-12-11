import sys

if sys.version_info[0] > 2:
    print("Python 3.x is not supported. Please retry with Python 2.x")
    sys.exit(1)
else:
    import scrabble_gui
    if __name__ == '__main__':
        scrabble_gui.main()
    
