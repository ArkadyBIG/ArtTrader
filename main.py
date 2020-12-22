from niftygateway_parser import NiftygatewayParser, Offer
from telegram_manager import telegram_manager
from threading import Thread
from time import sleep
from datetime import datetime
from database import DataBase
from typing import List


def make_markup_valid(text: str):
    return text.replace('.', r'\.').replace(')', r'\)').replace('(', r'\(').replace('-', r'\-')

class ArtTrader:
    def __init__(self):
        self._last_parse = datetime.min
        self._parser = NiftygatewayParser()
        self._database = DataBase()
        self._telegram_manager = telegram_manager
        
        self._telegram_manager.set_force_parse_command(self.force_parse)
        self._telegram_manager.set_database(self._database)
        self._telegram_manager.set_list_command(self._list_command)
        self._telegram_manager.set_last_parsed_command(self._last_parse_command)
        
        
        self._polling_thread = None
        self._force_parse = False
        self._list_offers = False
            
    def pooling(self, thread=False):
        if thread:
            self._polling_thread = Thread(target=self._telegram_manager.polling, 
                                        daemon=1)
            self._polling_thread.start()
        else:
            self._telegram_manager.polling()
    
    def force_parse(self):
        self._force_parse = True
    
    def parse_and_send(self, notify_subscribers=True):
        price = self._telegram_manager.max_price
        if notify_subscribers:
            self.send_progress_info(0, 100, None, price, False)
        
        on_pool = self.send_progress_info if notify_subscribers else None 
        offers = self._parser.get_offers(price, on_pool)
        if notify_subscribers:
            self.send_progress_info(0, 0, offers, price, finished=True)

        offers = [o for o in offers if 
                  self._database.insert_offer(o.token_id, o.contract_address, o.price, o.description)]
        if offers:
            self.send_offers(offers)
        # else:
            # self.se
    
    def send_offers(self, offers: List[Offer]):
        if offers:
            list_offers = (offers[i: i + 50] for i in range(0, len(offers), 50))
            for chunk_offers in list_offers:
                msg = '\n\n'.join((self.to_message_text(o) for o in chunk_offers))
                self._telegram_manager.send_to_subscribers(msg, markdown=True)
        
    def parsing(self, interval=3600):
        while True:
            if self._force_parse or \
            (datetime.now() - self._last_parse).total_seconds() > interval:
                self.parse_and_send(self._force_parse)
                self._force_parse = False
                self._last_parse = datetime.now()
            
            if self._list_offers:
                self.list_command()
            sleep(5)

    @classmethod
    def to_message_text(cls, offer):
        text = '%s %s$' % (offer.description, f'{offer.price:.2f}' )
        return '[%s](%s)' % (make_markup_valid(text), offer.url)

    def list_command(self):
        self._list_offers = False
        offers = self._database.get_offers(self._telegram_manager.max_price)
        offers = [Offer(token_id=i[0], contract_address=i[1], 
                        price=i[2], description=i[3]) for i in offers]
        self.send_offers(offers)
    
    def _list_command(self):
        self._list_offers = True
    
    def _last_parse_command(self):
        mins = (datetime.now() - self._last_parse).total_seconds() // 60
        if mins > 100_000:
            mins = 0
        self._telegram_manager.send_to_subscribers('Last parsed: %i minutes ago' % mins)
    
    def send_progress_info(self, current_page, pages_count, offers, max_price, edit_previous=True, finished=False):
        if not finished:
            msg = f'Pages parsed {current_page} / {pages_count}\n'
        else:
            msg = 'Finished parsing\n'
        msg += f'Price limit {max_price}$\n\n'
        self._telegram_manager.send_progress_info(
            msg,
            edit_previous=edit_previous)
    
    def close(self):
        self._telegram_manager.stop()
        self._parser.close()
        self._database.close()

def main():
    # try:
    trader = ArtTrader()
    trader.pooling(thread=True)
    trader.parsing()
    # finally:
    trader.close()
    
    
if __name__ == "__main__":
    main()
    








