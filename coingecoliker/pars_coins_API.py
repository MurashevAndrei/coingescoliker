import run_coins_pars_API as get_coins
import pars_coins_markets as get_markets
import parse_coins_detail as get_details

if __name__ == '__main__':
    get_coins.run_parser()
    get_markets.main()
    get_details.main()
