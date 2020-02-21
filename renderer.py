import curses
from typing import List

from data_retriever import lookup_addresses
from wallet import Wallet

# to be initialized by init_render
attributes = {}

ADD = 0
MANAGE_COIN = 1
REFRESH = 2
DELETE_WALLET = 3
EXIT = 4
MAIN_OPTIONS = ["Add coin", "Manage coin", "Refresh", "Delete wallet", "Exit"]

REMOVE_ADDRESSES = 0
REMOVE_MANUAL_BALANCE = 1
DELETE_COIN = 2
RETURN = 3
MANAGE_COIN_OPTIONS = ["Remove addresses", "Remove manual balance", "Delete coin", "Return"]

MAX_ADDRESS_LEN = 45

ENTER = 10
ESCAPE = 27

Y = 0
X = 1
HEADER_START = (2, 5)
SUB_MENU_START = (4, 2)


def init_render(stdscr):
    """
    Initializes parameters needed for working with curses. must be called before calling functions
    from this file
    In addition presents the main header and a loading banner
    """
    curses.curs_set(0)  # hide the cursor
    
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    attributes['normal'] = curses.color_pair(1)
    
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
    attributes['highlighted'] = curses.color_pair(2)
    
    # set foreground and background colors to normal
    stdscr.bkgd(' ', attributes['normal'])
    
    main_header(stdscr)
    stdscr.addstr(SUB_MENU_START[Y], SUB_MENU_START[X], "Loading...")
    stdscr.refresh()


def main_header(stdscr):
    stdscr.erase()
    stdscr.border()
    stdscr.addstr(HEADER_START[Y], HEADER_START[X],
                  "CryptoWatch - Multi Cryptocurrency watch-only wallet", curses.A_UNDERLINE)


def display_options_bar(stdscr, y, x, options, highlight=-1, layout='vertical'):
    """
    Display options bar in row y starting from cell x

    :param options list of strings - the options to display
    :param highlight index of an option to highlight.
    :param y base row number
    :param x base column number
    :param layout how the options should be display. should be 'vertical' or 'horizontal'.
                  in vertical mode, each row starts with a number (sequentially)

    """
    if layout == 'vertical':
        for i in range(len(options)):
            if i == highlight:
                attr = attributes['highlighted']
            else:
                attr = attributes['normal']
            stdscr.addstr(y, x, str(i + 1) + '. ')
            stdscr.addstr(options[i], attr)
            y += 1
    
    elif layout == 'horizontal':
        for i in range(len(options)):
            if i == highlight:
                attr = attributes['highlighted']
            else:
                attr = attributes['normal']
            stdscr.addstr(y, x, options[i], attr)
            x += len(options[i]) + 2


ASCII_1 = 49
ASCII_9 = 57


def read_option(stdscr, option, num_options, layout='vertical'):
    """
    track the user clicks to navigate between options on screen

    :param option the currently chosen option
    :param num_options total number of options in the options bar
    :param layout 'vertical' or 'horizontal'. determines the navigation keys (up/down or left/right)
    :return: a tuple (c, p) where c is the last pressed button, and p is the new current option
    """
    
    if layout == 'vertical':
        decrement_key = curses.KEY_UP
        increment_key = curses.KEY_DOWN
    elif layout == 'horizontal':
        decrement_key = curses.KEY_LEFT
        increment_key = curses.KEY_RIGHT
    else:
        raise ValueError("Wrong parameter for 'layout' in read_option()")
    
    c = stdscr.getch()
    if c == decrement_key and option > 0:
        return c, option - 1
    elif c == increment_key and option + 1 < num_options:
        return c, option + 1
    elif ASCII_1 <= c <= ASCII_9 and c - ASCII_1 < num_options:
        # user click a number between 1 and 9 and this is a legal option
        return c, c - ASCII_1
    return c, option


COLUMNS_SPACE = 12


def display_coins_table(stdscr, y, x, coins):
    """
    Display the coins table starting from row y and column x.

    :param coins List of lists. each inner list is
                [coin_id, amount, value_usd, value_btc, unit_value_usd]

    number of lines written to screen is len(coins)+3
    """
    coins.sort(key=lambda coin: coin[0])  # sort by coin_id alphabetically
    
    stdscr.addstr(y, x, "Coin        Amount      USD-value   BTC-value",
                  attributes['highlighted'])
    if len(coins) == 0:
        stdscr.addstr(y + 1, x, "Your wallet is empty. Choose 'Add' to add new coin")
        return
    
    for i, coin in enumerate(coins):
        # print line for a single coin
        for j in range(len(coin)):
            stdscr.addstr(y + 1 + i, x + (j * COLUMNS_SPACE), str(coin[j]))
    
    total_usd = 0
    total_btc = 0
    for i in range(len(coins)):
        if coins[i][2] != 'N/A' and coins[i][3] != 'N/A':
            # actually it is guaranteed that both will be 'N/A', or both won't
            total_usd += coins[i][2]
            total_btc += coins[i][3]
    
    # truncate digits after point
    total_usd = float('%.3f' % total_usd)
    total_btc = float('%.8f' % total_btc)
    
    stdscr.addstr(y + len(coins) + 2, x, "Total Balance: ")
    stdscr.addstr("{0} USD, {1} BTC".format(total_usd, total_btc))


def display_main_scr(stdscr, coins, option=0):
    """
    Display the main screen - a table with all coins and amounts, and list of options

    :param coins: list of lists. Each inner list correspond to a single coin
                  and looks like this: [coin_code, amount, value_in_usd, value_in_btc]
    :param option the option to be initially chosen
    :return: the option chosen by the user
    """
    
    c = 0  # last character read
    should_render = True
    
    while c != ENTER:
        if should_render:
            main_header(stdscr)
            display_coins_table(stdscr, SUB_MENU_START[Y], SUB_MENU_START[X], coins)
            display_options_bar(stdscr, SUB_MENU_START[Y] + len(coins) + 5, SUB_MENU_START[X],
                                MAIN_OPTIONS, highlight=option, layout='horizontal')
            should_render = False
        
        c, new_option = read_option(stdscr, option, len(MAIN_OPTIONS), 'horizontal')
        if new_option != option or c == curses.KEY_RESIZE:
            option = new_option
            should_render = True
    
    return option


def read_address_from_user(stdscr):
    """
    read comma separated addresses from the user.

    :return: list of all the addresses
    """
    addresses = stdscr.getstr().decode("utf-8")
    addresses = "".join(addresses.split())  # remove any whitespaces
    return addresses.split(',')


def add_menu_header(stdscr):
    """
    Displays the header for the add coin menu
    """
    main_header(stdscr)
    stdscr.addstr(SUB_MENU_START[Y], SUB_MENU_START[X], "Add coin:")
    stdscr.refresh()


def display_add_scr(stdscr, wallet: Wallet):
    """
    Display the 'add coin' screen to the user and handles adding new coin

    :param wallet: Wallet object to which coins should be added
    :param y_base the first row to draw from
    :param x_base the first column to draw from
    """
    c = 0  # last character read
    option = 0
    
    while c != ESCAPE and c != ENTER:
        add_menu_header(stdscr)
        display_options_bar(stdscr, SUB_MENU_START[Y], SUB_MENU_START[X],
                            ["Add addresses to watch", "Add balance manually"], option, 'vertical')
        c, option = read_option(stdscr, option, 2, 'vertical')
    
    if c == ESCAPE:
        return
    
    last_line = SUB_MENU_START[Y]  # the last line we wrote to
    try:
        curses.echo()  # so the user sees what he types
        curses.curs_set(1)
        
        add_menu_header(stdscr)
        stdscr.addstr(last_line + 2, SUB_MENU_START[X],
                      "Enter coin code/symbol (e.g. BTC): ")
        last_line += 2
        coin_code = stdscr.getstr().decode("utf-8").upper()
        
        if option == 0:
            stdscr.addstr(last_line + 2, SUB_MENU_START[X],
                          "Enter addresses to watch (comma separated, e.g. addr1,addr2,addr3):")
            last_line += 2
            stdscr.move(last_line + 1, SUB_MENU_START[X])
            last_line += 1
            addresses = read_address_from_user(stdscr)
            wallet.add_addresses(coin_code, addresses)
        else:
            # manually add balance
            stdscr.addstr(last_line + 2, SUB_MENU_START[X], "Enter amount to add: ")
            last_line += 2
            amount = float(stdscr.getstr().decode("utf-8"))
            wallet.add_manual_balance(coin_code, amount)
        
        curses.curs_set(0)
        curses.noecho()
    except Exception:
        curses.curs_set(0)
        curses.noecho()
        return None


def display_addresses_list(stdscr, addresses, balances, base_y, base_x, highlight=-1):
    """
    Display a list of addresses and their balances, starting from point (base_y, base_x)
    writes exactly len(addresses)+1 lines

    :param stdscr:
    :param addresses: the addresses to print
    :param balances: the balances correspond to the addresses
    :param highlight index of an address to highlight. by default no address is highlighted

    """
    # write the head of the table:   Address                  Balance
    stdscr.addstr(base_y, base_x, "Address", curses.A_UNDERLINE)
    stdscr.addstr(base_y, base_x + MAX_ADDRESS_LEN + 2, "Balance",
                  curses.A_UNDERLINE)
    
    y = base_y + 1  # the next line to write to
    # write all addresses with their balances
    for i, (addr, balance) in enumerate(zip(addresses, balances)):
        if i == highlight:
            attr = attributes['highlighted']
        else:
            attr = attributes['normal']
        stdscr.addstr(y, base_x, addr, attr)
        if balance < 0:
            stdscr.addstr(y, base_x + MAX_ADDRESS_LEN + 2, 'N/A')
        else:
            stdscr.addstr(y, base_x + MAX_ADDRESS_LEN + 2, '%.8f' % balance)
        y += 1


def remove_addresses_scr(
    stdscr,
    coin: str,
    addresses: List[str],
    balances: List[float],
    wallet: Wallet,
):
    """
    Display the remove addresses screen. Let the user choose addresses to remove

    `addresses` is a list of addresses of the given coin
    `balances` is a list of the corresponding balances for the addresses
    """
    c = 0
    option = 0
    base_y = SUB_MENU_START[Y]
    base_x = SUB_MENU_START[X]
    should_render = True
    while True:
        while c != ENTER and c != ESCAPE:
            if should_render:
                main_header(stdscr)
                stdscr.addstr(base_y, base_x, "Remove " + coin + " addresses:")
                stdscr.addstr(base_y + 1, base_x, "Click on an address to remove it")
                display_addresses_list(stdscr, addresses, balances, base_y + 2, base_x, option)
                
                # the Done 'button'
                if option == len(addresses):
                    # the Done button is marked
                    attr = attributes['highlighted']
                else:
                    attr = attributes['normal']
                stdscr.addstr(base_y + 2 + len(addresses) + 2, base_x, "Done", attr)
                
                should_render = False
            
            c, new_option = read_option(stdscr, option, len(addresses) + 1, layout='vertical')
            # the +1 in num_options is for the 'Done' button
            
            if new_option != option:
                option = new_option
                should_render = True
        
        if c == ESCAPE or option == len(addresses):
            # escaped pressed or 'Done' button clicked
            return
        else:
            # address to remove was chosen
            wallet.remove_watch_address(coin, [addresses[option]])
            addresses.pop(option)
            balances.pop(option)
            if len(addresses) == 0:  # all addresses were removed
                return
            elif len(addresses) == option:
                # the last address was removed, so mark the one above it
                option -= 1
            should_render = True
        
        c = 0


def manage_coin(stdscr, coin: str, wallet: Wallet):
    """
    Display a manage screen for a specific coin

    :param coin: the coin to manage
    :param wallet: wallet object
    """
    c = 0
    option = 0
    tracked_coin = wallet.get_coin_info(coin)
    addresses_list = list(tracked_coin.addresses)
    balances = lookup_addresses(coin, addresses_list)
    manual_balance = tracked_coin.manual_balance
    base_x = SUB_MENU_START[X]
    base_y = SUB_MENU_START[Y]
    
    while True:
        should_render = True
        while c != ENTER and c != ESCAPE:
            if should_render:
                main_header(stdscr)
                stdscr.addstr(base_y, base_x, coin + " in wallet:")
                if balances is None:
                    balances = [-1] * len(addresses_list)
                display_addresses_list(stdscr, addresses_list, balances, base_y + 2, base_x)
                y = base_y + 2 + len(addresses_list) + 2  # the next line to write to
                if manual_balance != 0:
                    stdscr.addstr(y, base_x, "Manual balance: " + ('%.8f' % manual_balance))
                    y += 2
                display_options_bar(stdscr, y, base_x, MANAGE_COIN_OPTIONS,
                                    highlight=option, layout='horizontal')
                should_render = False
            
            c, new_option = read_option(stdscr, option, len(MANAGE_COIN_OPTIONS), 'horizontal')
            if new_option != option:
                option = new_option
                should_render = True
        
        if c == ESCAPE or option == RETURN:
            return
        
        if option == REMOVE_ADDRESSES:
            remove_addresses_scr(stdscr, coin, addresses_list, balances, wallet)
            # addresses may have changed. get updated info
            tracked_coin = wallet.get_coin_info(coin)
            balances = lookup_addresses(coin, list(tracked_coin.addresses))
        elif option == REMOVE_MANUAL_BALANCE:
            wallet.remove_manual_balance(coin)
            manual_balance = 0
        elif option == DELETE_COIN:
            wallet.remove_coin(coin)
            return
        c = 0


def manage_scr(stdscr, wallet):
    """
    Display the manage coins screen
    """
    coins = wallet.get_coins_ids()
    c = 0
    option = 0
    while c != ENTER and c != ESCAPE:
        main_header(stdscr)
        stdscr.addstr(SUB_MENU_START[Y], SUB_MENU_START[X], "Choose coin to manage:")
        display_options_bar(stdscr, SUB_MENU_START[Y] + 2, SUB_MENU_START[X],
                            coins, highlight=option, layout='vertical')
        c, option = read_option(stdscr, option, len(coins), 'vertical')
    
    if c == ESCAPE:
        return
    
    manage_coin(stdscr, coins[option], wallet)
