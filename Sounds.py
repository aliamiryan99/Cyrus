import winsound


def end_beep():
    winsound.Beep(450, 1200)
    winsound.Beep(650, 2000)


end_beep()