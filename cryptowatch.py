#!/usr/bin/env python3

from curses import wrapper
import renderer
import wallet as Wallet


def run_crypto_watch(stdscr):
    renderer.init_render(stdscr)
    wallet = Wallet.Wallet()
    option = renderer.ADD
    refresh = True
    while option != renderer.EXIT:
        if refresh:
            coins = wallet.get_balances()
            refresh = False
        option = renderer.display_main_scr(stdscr, coins, option=option)
        if option == renderer.ADD:
            renderer.display_add_scr(stdscr, wallet)
        elif option == renderer.MANAGE_COIN:
            renderer.manage_scr(stdscr, wallet)
        elif option == renderer.REFRESH:
            refresh = True
        elif option == renderer.DELETE_WALLET:
            wallet.delete()


# wrapper will initialize the screen, turn off keys echoing, turn on
# cbreak (response immediately upon key press), and on exit - restore the default
# settings for the terminal
wrapper(run_crypto_watch)
