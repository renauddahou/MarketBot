import os
import sqlite3
import telebot
import time
import random
from telebot import types
import urllib.request as urllib
import requests.exceptions as r_exceptions
from requests import ConnectionError
import pdb

import const, base, markups, temp, config

bot = telebot.TeleBot(const.token)
uploaded_items = {}


# u "Manipulation de la commande /start - branchement des utilisateurs en acheteur et vendeur"
@bot.message_handler(commands=['start'])
def start(message):
    base.add_user(message)
    if base.is_seller(message.from_user.id):
        bot.send_message(message.chat.id, const.welcome_celler, reply_markup=markups.start())
    else:
        bot.send_message(message.chat.id, const.welcome_client, reply_markup=markups.start1())


# Affichage d'un menu avec les types de produits
@bot.message_handler(regexp=u"Menu")
def client_panel(message):
    bot.send_message(message.chat.id, u'Sélectionner une catégorie:', reply_markup=markups.start1())


@bot.message_handler(func=lambda message: message.text in const.messages.keys())
def handle_stand_msgs(message):
    bot.send_message(message.chat.id, const.messages[message.text])


@bot.callback_query_handler(func=lambda call: call.data == 'client_panel')
def client_panel(call):
    bot.edit_message_text(const.welcome_client, chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(chat_id=call.message.chat.id, text='...', reply_markup=markups.start1())


# Exécution du gestionnaire des fournisseurs
@bot.callback_query_handler(func=lambda call: call.data == 'celler_panel')
def celler_panel(call):
    bot.edit_message_text(u'Admin.Sélectionnez une action.', call.message.chat.id, call.message.message_id,
                          parse_mode='Markdown', reply_markup=markups.edit())


@bot.callback_query_handler(func=lambda call: call.data == 'retrieve')
def handle_retrieve(call):
    bot.send_message(call.message.chat.id, "TextHere", reply_markup=telebot.types.InlineKeyboardMarkup().row(
        telebot.types.InlineKeyboardButton('В меню', callback_data="menu")))


@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def handle_reieve(call):
    send_menu(call.message)


def spamm(message):
    for i in base.get_users():
        try:
            bot.send_message(i[0], message.text)
        except Exception:
            continue


@bot.message_handler(commands=['mail'])
def mail_spam(message):
    print('here', message.chat.id, const.admin_id)
    if int(message.chat.id) == int(const.admin_id):
        msg = bot.send_message(message.chat.id, "Rédiger un message pour le bulletin d'information")
        bot.register_next_step_handler(msg, spamm)


@bot.message_handler(regexp=const.menu_name)
def handle_rer(message):
    print('here')
    send_menu(message)


@bot.message_handler(func=lambda message: message.text in const.types.keys())
def handle_fast(message):
    bot.send_message(message.chat.id, const.msgs[message.text])
    for item in base.type_finder(const.types[message.text]):
        uploaded_items[str(item.id)] = 0
        mark = telebot.types.InlineKeyboardMarkup().row(
            telebot.types.InlineKeyboardButton('Перейти', callback_data='retrieve'))
        try:
            url = item.url
            photo = open("temp.jpg", 'w')  # u"Initialisation du fichier"
            photo.close()
            photo = open("temp.jpg", 'rb')
            urllib.urlretrieve(url, "temp.jpg")
            bot.send_photo(chat_id=message.chat.id, photo=photo)
            bot.send_message(message.chat.id, item.description, markup=mark)
            photo.close()
            os.remove("temp.jpg")
        except Exception:
            bot.send_message(message.chat.id, item.description, reply_markup=mark)


# Se déplacer dans les catégories
def send_menu(message):
    bot.send_message(message.chat.id, 'Sélectionnez la catégorie souhaitée.', reply_markup=markups.show_types(message.chat.id))


def handle_price(message):
    if not message.text.isdigit():
        msg = bot.send_message(message.chat.id, 'Invalid input data, try again...')
        bot.register_next_step_handler(msg, handle_price)
        return 0
    bot.send_message(const.admin_id, ";".join([message.text, str(message.chat.id)]))
    bot.send_message(message.chat.id, text=u'Le numéro de réserve de votre panier personnel pendant 30 minutes: 1ae085ae-667c'.format(
        message.chat.id) + '-4155-bb9e-e84c6a7053c'.format(chat_id=message.chat.id) + '4\n'
                                                                                      "Vous recevrez toutes les informations relatives à votre commande dès que vous l'aurez payée.\n"
                                                                                      'Montant du paiement = %d'
                                                                                      '--------------------------------\n'
                                                                                      'Détails pour le paiement BTC:\n'
                                                                                      'Votre numéro de portefeuille personnel BTC:1MqXiJi9zq7esyKHbiUNTxSss8WQRKYYqP\n'
                                                                                      "Après avoir reçu 1 confirmation par le réseau, le Bot vous demandera votre numéro d'article. Entrez-le dans le format 578040. L'adresse vous sera alors communiquée immédiatement.\n"
                                                                                      '--------------------------------\n'
                                                                                      'Le montant du paiement doit être le montant indiqué par le vendeur. Sinon, votre paiement ne sera pas automatiquement crédité\n'
                                                                                      "Il est important de payer les marchandises réservées dans le délai imparti, sinon votre commande sera annulée. Lorsque la période de réservation arrive à son terme, le système vous demandera de prolonger la réservation d'une demi-heure supplémentaire.\n"
                                                                                      "Après avoir reçu le produit, vous pouvez laisser des commentaires sur le produit ou le vendeur à l'adresse  en écrivant à .... support, en mentionnant votre numéro de réserve de panier personnel.\n"
                                                                                      'Si nécessaire, vous pouvez annuler la réserve du panier en appuyant sur le bouton "Annuler".' % (
                                                   int(message.text) * 1.10), parse_mode='HTML',
                     reply_markup=telebot.types.InlineKeyboardMarkup().row(
                         telebot.types.InlineKeyboardButton('Проверить', callback_data='check'), telebot.types.InlineKeyboardButton('Annulation', callback_data='quitter')))


bot.callback_query_handler(func=lambda call: call.data == 'quit')
def quit_pricing(call):
    print('her')
    bot.edit_message_text(const.quit_text, call.message.chat.id,
                          call.message.message_id)

# u"Afficher les marchandises et les mettre en cache"
@bot.callback_query_handler(func=lambda call: call.data in base.give_menu())
def show_items(call):
    for item in base.type_finder(call.data):
        key = item.get_desc2()
        uploaded_items[str(item.id)] = 0
        print(uploaded_items)
        try:
            url = item.url
            photo = open("temp.jpg", 'w')  # u"Initialisation du fichier"
            photo.close()
            photo = open("temp.jpg", 'rb')
            urllib.urlretrieve(url, "temp.jpg")
            bot.send_photo(chat_id=call.message.chat.id, photo=photo)
            msg = bot.send_message(call.message.chat.id, item.description, reply_markup=key)
            photo.close()
            os.remove("temp.jpg")
        except Exception:
            msg = bot.send_message(call.message.chat.id, item.description, reply_markup=key)


@bot.callback_query_handler(func=lambda call: call.data.startswith('p'))
def handle_your_price(call):
    msg = bot.send_message(call.message.chat.id, '"Ecrivez votre prix')
    bot.register_next_step_handler(msg, handle_price)


@bot.callback_query_handler(func=lambda call: call.data == 'check')
def handle_your_price(call):
    bot.send_message(call.message.chat.id, 'Thisistext', reply_markup=telebot.types.InlineKeyboardMarkup().row(
        telebot.types.InlineKeyboardButton('Проверить', callback_data='check')))


# u"Traitement du premier achat d'un article"
@bot.callback_query_handler(func=lambda call: call.data in uploaded_items)
def callback_handler(call):
    uploaded_items[str(call.data)] += 1
    print('uploaded_items : ' + str(uploaded_items))
    print('callback_handler.call.data = ' + str(call.data))
    markup = markups.add(call.data)
    a = random.randint(50000, 100000)
    bot.send_message(chat_id=call.message.chat.id,
                     text=u'Le numéro de réserve de votre panier personnel pendant 30 minutes: 1ae085ae-667c'.format(
                         chat_id=call.message.chat.id) + str(a) + '-4155-bb9e-e84c6a7053c'.format(
                         chat_id=call.message.chat.id) + str(a) + '4\n'
                                                                  "Vous recevrez toutes les informations relatives à votre commande dès que vous l'aurez payée.\n"
                                                                  '--------------------------------\n'
                                                                  'Détails pour le paiement BTC:\n'
                                                                  'Votre numéro de portefeuille personnel BTC:  1MqXiJi9zq7esyKHbiUNTxSss8WQRKYYqP\n'
                                                                  "Après avoir reçu 1 confirmation par le réseau, le Bot vous demandera votre numéro d'article. Entrez-le dans le format 578040. L'adresse vous sera alors communiquée immédiatement.\n"
                                                                  '--------------------------------\n'
                                                                  'Le montant du paiement doit être le montant indiqué par le vendeur. Sinon, votre paiement ne sera pas automatiquement crédité.\n'
                                                                  "Il est important de payer les marchandises réservées dans le délai imparti, sinon votre commande sera annulée. Lorsque la période de réservation arrive à son terme, le système vous demandera de prolonger la réservation d'une demi-heure supplémentaire.\n"
                                                                  "Après avoir reçu le produit, vous pouvez laisser des commentaires sur le produit ou le vendeur à l'adresse en écrivant à... support, en mentionnant votre numéro de réserve de portefeuille personnel.\n"
                                                                  'Si nécessaire, vous pouvez annuler la réserve du panier en appuyant sur le bouton Annuler"',
                     parse_mode='HTML', reply_markup=markup)


# La réponse "payé" à la question sur le paiement


#Vient ensuite la zone d'administration----------------------------------------


# Ajouter une catégorie
@bot.callback_query_handler(func=lambda call: call.data == 'add_kat')
def handle_add_kat(call):
    sent = bot.send_message(call.message.chat.id, "Entrez un nom de catégorie", reply_markup=markups.return_to_menu())
    bot.register_next_step_handler(sent, base.add_kat)


# Suppression d'une catégorie
@bot.callback_query_handler(func=lambda call: call.data == 'delete_kat')
def handle_delete_kat(call):
    bot.edit_message_text("Sélectionnez une catégorie à supprimer", call.message.chat.id,
                          call.message.message_id, reply_markup=markups.delete_kat())


@bot.callback_query_handler(func=lambda call: call.data[0] == '?')
def handle_delete_this_kat(call):
    db = sqlite3.connect("clientbase.db")
    cur = db.cursor()
    cur.execute("DELETE FROM categories WHERE name = ?", (str(call.data[1:]),))
    db.commit()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.delete_kat())
    print('deleted')


# Ajout d'un produit.


# Выбор типа товара
@bot.callback_query_handler(func=lambda call: call.data == 'add_item')
def handle_add_item_type(call):
    new_item = temp.Item()
    const.new_items_user_adding.update([(call.message.chat.id, new_item)])
    sent = bot.send_message(call.message.chat.id, "Sélectionnez le type de produit:", reply_markup=markups.add_item())
    bot.register_next_step_handler(sent, base.add_item_kategory)
    const.user_adding_item_step.update([(call.message.chat.id, "Enter name")])


# Saisir un nom de produit
@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "Enter name")
def handle_add_item_description(message):
    sent = bot.send_message(message.chat.id, "Entrez une description")
    bot.register_next_step_handler(sent, base.add_item_description)
    const.user_adding_item_step[message.chat.id] = "End"


# Fin de l'ajout du produit
@bot.message_handler(func=lambda message: base.get_user_step(message.chat.id) == "End")
def handle_add_item_end(message):
    bot.send_message(message.chat.id, "Ajouté!\nMenu :", reply_markup=markups.show_types(message.chat.id))
    const.user_adding_item_step.pop(message.chat.id)


# Suppression d'un produit
@bot.callback_query_handler(func=lambda call: call.data == 'delete_item')
def handle_delete_item(call):
    bot.edit_message_text("Choisissez un produit à enlever", call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.delete_item(call.message.chat.id))


@bot.callback_query_handler(func=lambda call: call.data[0] == '^')
def handle_delete_from_db(call):
    db = sqlite3.connect("clientbase.db")
    cur = db.cursor()
    cur.execute("DELETE FROM items WHERE id = ?", (str(call.data[1:]),))
    db.commit()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.delete_item(call.message.chat.id))
    print('deleted')


@bot.message_handler(content_types=['text'])
def bank(message):
    markup_start = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup_start.row("Comment ça marche", "Passer une commande")
    markup_start.row("Feedback", "Support")
    markup_start.row('Devenir un vendeur')
    keyboard1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard1.row("Passer une commande", "Commentaires")
    keyboard1.row("Support", "Devenir vendeur")
    keyboard3 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard3.row("Comment ça marche", "Passer une commande")
    keyboard3.row("Support", "Devenir vendeur")
    keyboard4 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard4.row("Comment ça marche", "Passer une commande".)
    keyboard4.row("Commentaire", "Devenir vendeur".)
    keyboard5 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard5.row("Comment ça marche", "Passer une commande".)
    keyboard5.row('Feedback', 'Support')
    markup_oplata = types.InlineKeyboardMarkup()
    markup_oplata.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['Купить']])
    if message.text == 'Comment ça marche':
        print('Как работает')
        bot.send_message(message.chat.id,
                         "Le service est entièrement automatisé, de sorte que le processus, de l'achat à la collecte, ne dure pas plus d'une heure.\n"
                         "Pour passer une commande, il vous suffit d'aller sur 'Passer une commande', d'indiquer votre ville et le robot trouvera automatiquement les vendeurs de notre plateforme dans votre ville et vous montrera les produits disponibles.\n"
                         'Après avoir sélectionné un article, vous recevrez des informations personnelles pour le paiement. Notre site supporte 2 méthodes de paiement : cash et Btc, chaque vendeur mettra ses détails, ainsi certains articles ne peuvent être achetés que pour cash ou seulement pour Btc.\n'
                         'Lorsque vous payez sur le compte cash, veillez à indiquer votre surnom Telegram au format @vous dans le commentaire du paiement. Sinon, le paiement ne sera pas crédité automatiquement.\n'
                         "Lorsque vous payez en Btc, l'adresse du portefeuille Btc qui vous a été donnée est liée à votre pseudo Telegram. Après avoir reçu 1 confirmation, le Bot confirmera automatiquement la réception des fonds et vous demandera le numéro de l'article. Entrez-le dans le format 578040.\n"
                         "Après avoir effectué le transfert, cliquez sur le bouton 'J'ai payé', le robot vérifiera automatiquement votre paiement et vous donnera l'adresse du trésor avec toutes les informations supplémentaires (cela dépend du vendeur et de ses chasseurs de trésors).\n"
                         'Vous pouvez laisser des commentaires sur le produit ou le vendeur  en écrivant à ... avec votre numéro de réserve personnel.',
                         parse_mode='HTML', reply_markup=keyboard1)
    if message.text == 'Commentaires':
        print('Commentaires')
        bot.send_message(message.chat.id,
                         'Vous trouverez toutes les informations nécessaires sur le fonctionnement du bot automatique dans les forums:\n'
                         'http://ramp24vqtden6hep.onion/info\n'
                         'http://lkncc.cc/newrampbot\n'
                         'http://leomarketjdridoo.onion/newrampbot\n'
                         'http://eeyovrly7charuku.onion/newrampbot\n'
                         'http://tochka3evjl3sxdv.onion/newrampbot\n'
                         "Vous pouvez également laisser des commentaires sur le produit ou le détaillant à l'adresse .... avec votre numéro de réserve personnel.",
                         parse_mode='HTML', reply_markup=keyboard3)
    if message.text == 'Support':
        print('Support')
        bot.send_message(message.chat.id,
                         "Si vous rencontrez des difficultés pour payer ou récupérer un colis, ou si vous avez des questions sur le fonctionnement du bot, vous pouvez contacter l'équipe d'assistance de @equipe sur Telegram @equipe.",
                         parse_mode='HTML', reply_markup=keyboard4)
    if message.text == 'Devenir un vendeur':  # К ЭТОЙ КНОПКЕ НУЖНО ПОДРУБИТЬ ФОТО И ВИДЕО
        print('Devenir un vendeur')
        bot.send_message(message.chat.id,
                         'Pour devenir vendeur sur notre site, vous devez acheter un tarif mensuel de vendeur ou un tarif à vie de vendeur.\n'
                         'Frais de connexion:\n'
                         "5000 francs par mois avec possibilité d'extension du tarif à la durée de vie.\n"
                         '50000 francs-prix du vendeur à vie.\n'
                         'Ce prix comprend:\n'
                         "Panneau d'administration pratique avec la possibilité de publier des articles avec des photos (version WEB uniquement), d'ajouter vos coordonnées et des adresses de signets prêtes à l'emploi directement depuis la messagerie Telegram.\n"
                         'Assistance aux fournisseurs 24 heures sur 24 et 7 jours sur 7.\n'
                         'Pas de commissions supplémentaires, le paiement des marchandises se fait uniquement sur vos comptes ou portefeuilles.\n'
                         "Afin d'activer le tarif du vendeur, vous devez effectuer un transfert vers notre compte Qiwi Wallet +79619218391 avec votre surnom Telegram au format @helpramp en commentaire du paiement.\n"
                         "Après avoir effectué le paiement, vous serez contacté par notre agent d'assistance technique.", parse_mode='HTML',
                         reply_markup=keyboard5)
    if message.text == 'Passer une commande':
        print('Passer une commande')
        sent = bot.send_message(message.chat.id, 'Entrez votre ville dans le format #Ville')
        bot.register_next_step_handler(sent, hello)
    if message.text == 'Feedback':
        print('Feedback')
        bot.send_message(message.chat.id, 'Sélectionnez le bouton.', parse_mode='HTML', reply_markup=markup_start)


# Запуск бота
while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except ConnectionError as expt:
        config.log(Exception='HTTP_CONNECTION_ERROR', text=expt)
        print('Connection lost..')
        time.sleep(30)
        continue
    except r_exceptions.Timeout as exptn:
        config.log(Exception='HTTP_REQUEST_TIMEOUT_ERROR', text=exptn)
        time.sleep(5)
        continue
