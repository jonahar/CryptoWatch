#!/usr/bin/env python3

from curses import wrapper
import renderer
import wallet as Wallet


def run_crypto_watch(stdscr):
    renderer.init_render(stdscr)
    wallet = Wallet.Wallet()
    option = 0
    while True:
        coins = wallet.get_balances()
        option = renderer.display_main_scr(stdscr, coins, option=option)
        if option == renderer.ADD:
            renderer.display_add_scr(stdscr, wallet)
        elif option == renderer.MANAGE_COIN:
            renderer.manage_scr(stdscr, wallet)
        elif option == renderer.REFRESH:
            pass  # coins will be refreshed in the next loop cycle
        elif option == renderer.DELETE_WALLET:
            wallet.delete()
        elif option == renderer.EXIT:
            return


# wrapper will initialize the screen, turn off keys echoing, turn on
# cbreak (response immediately upon key press), and on exit - restore the default
# settings for the terminal
wrapper(run_crypto_watch)
