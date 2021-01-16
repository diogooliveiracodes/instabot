from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

"""
Este protótpipo tem a finalidade de aumentar a quantidade de seguidores
de um determinado perfil do instagram de forma automatizada.

Antes de iniciar o script é necessário preencher as variáveis:
self.user_login - login do usuario que quer ganhar seguidores
self.user_password - senha do usuario que quer ganhar seguidores
self.profile_list - lista de perfis no instagram para seguir os seguidores

Etapas da rotina:
01. login() - Faz login no instagram com a conta e senha do usuário. 
02. search_profile() - Utilizando a lista self.profile_list abre a página do perfil e o remove da lista.
03. open_followers() - Abre a lista de seguidores.
04. sweep_followers() - Rola a barra de rolagem da tela de seguidores até o final.
05. follow() - Segue ordenadamente os seguidores, sempre saltando um deles sem seguir. 
06. close_followers_box() - Fecha a caixa de seguidores.
Finalmente a rotina recomeça com o próximo perfil da lista self.profile_list, sem repetir a Etapa 01 login().

Todas as etapas tem seu tratamento de erro com mensagens específicas.

Ao final de cada função e ao encerrar o script é exibida uma mensagem de sucesso.

"""

__author__= "Diogo Oliveira"
__date__ = "06/01/2020"
__version__ = "1.0.0"

PATH = "C:\Program Files (x86)\chromedriver.exe" # pega o path do executável do chrome driver

class InstaBot():
    def __init__(self):

        self.choose = '0'
        print('\n\nQual função deseja utilizar?\n[ 1 ] - Ganhar seguidores\n[ 2 ] - Deixar de seguir quem não te segue')
        while self.choose!= '1' and self.choose!='2':
            self.choose = input('\nDigite sua escolha [ 1 ou 2 ] :')
            if self.choose!= '1' and self.choose!='2':
                print('\nOpção inválida, escolha entre [ 1 ou 2 ]')

        self.driver = webdriver.Chrome(PATH)
        self.driver.get("https://instagram.com") # abre a página
        self.profile_list = ['_follow_for_follow_for_follow_', 'follow_follow_back___', 'followforfollow2k.20', 'follow.4.follow_3', 'follow.for.follow_097'] # lista de usuarios do instagram para seguir os seguidores
        self.user_login = "SEU_PERFIL" #usuario do instagram
        self.user_password = "SUA_SENHA" #senha do seu usuario do instagram
        self.number_to_follow = 2500 #numero de seguidores a ser seguido de cada perfil listado (este número será dividido por 2)
        self.followers = [] #lista de seguidores
        self.following = [] #lista de perfis seguidos
        self.unfollowers = ['lista', 'de', 'não', 'seguidores'] #lista perfis que não seguem de volta

        try:
            self.login(); sleep(4)
            if self.choose == '1':
                self.farm_followers()
            elif self.choose == '2':
                self.unfollow_unfollowers()
            sleep(50)
        except:
            print('\nErro na função Iniciar')
        print('\nFim do Script')
    
    def login(self):
        try:
            self.login = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input'))
            )
            self.login.send_keys(self.user_login) #preenche usuario
        except:
            print('\nErro ao preencher o login')
        try:
            self.senha = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input'))
            )
            self.senha.send_keys(self.user_password) #Preenche senha
            sleep(1)
        except:
            print('\nErro ao preencher a senha')
        try:
            self.entrar = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="loginForm"]/div/div[3]/button'))
            )
            self.entrar.click() #Clica no botão entrar
        except:
            print('\nErro ao clicar no botão Entrar')
        print('\nLOGIN REALIZADO COM SUCESSO')

    def search_profile(self):
        try:
            search = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/div/div/span[2]'))
            )
            search.click() #clica na barra de pesquisa para ativar o input de pesquisa
        except:
            print('\nErro ao clicar na barra de pesquisa')
        try:
            opened_search = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input'))
            )
            opened_search.send_keys(self.profile_list[0]) #digita na barra de pesquisa o perfil a ser pesquisado
            sleep(2)
            opened_search.send_keys(Keys.DOWN)
            sleep(2)
            opened_search.send_keys(Keys.ENTER)
            sleep(2)
        except:
            print('\nErro ao digitar perfil a ser pesquisado')
        self.profile_list.remove(self.profile_list[0]) #remove o perfil já pesquisado da lista self.profile_list
        print('\nPESQUISA DE PERFIL REALIZADA COM SUCESSO')

    def open_followers(self):
        try:
            followers = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a'))
            )
            followers.click()
        except:
            print('\nErro ao abrir seguidores')
        print('\nABERTURA DOS SEGUIDORES REALIZADA COM SUCESSO')

    def open_following(self):
        try:
            following = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a'))
            )
            following.click()
        except:
            print('\nErro ao abrir lista de perfis seguidos')
        print('\nABERTURA DE LISTA DE PERFIS SEGUIDOS REALIZADA COM SUCESSO')

    def sweep_followers(self):
        
        try:
            followers_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="isgrP"]'))
            )
            count = 0
            last_ht, ht = 0, 1
            while last_ht != ht:
                last_ht = ht
                sleep(1)
                ht = self.driver.execute_script("""
                    arguments[0].scrollTo(0, arguments[0].scrollHeight);
                    return arguments[0].scrollHeight;
                    """, followers_box)
                count+=1
                if count == 500:
                    print(count)
                    break
                else:
                    pass
        except:
            print('\nErro na função sweep_followers')
        print('\nVARREDURA DE SEGUIDORES REALIZADA COM SUCESSO')

    def sweep_all_followers(self):
            
        try:
            followers_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="isgrP"]'))
            )
            last_ht, ht = 0, 1
            while last_ht != ht:
                last_ht = ht
                sleep(1)
                ht = self.driver.execute_script("""
                    arguments[0].scrollTo(0, arguments[0].scrollHeight);
                    return arguments[0].scrollHeight;
                    """, followers_box)
        except:
            print('\nErro na função sweep_all_followers')
        print('\nVARREDURA DE SEGUIDORES REALIZADA COM SUCESSO')

    def follow(self): 
        try:
            for i in range(1, self.number_to_follow): #numero de seguidores a seguir de cada perfil da lista self.profile_list
                if (i%2==0):
                    try:
                        followers = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '/html/body/div[5]/div/div/div[2]/ul/div/li['+i.__str__()+']/div/div[2]/button'))
                        )
                        if followers.text == 'Seguir':
                            followers.click()
                            sleep(300)
                    except Exception:
                        pass
        except:
            print('\nErro na função follow')
        print('\nPERFIS SEGUIDOS COM SUCESSO')

    def close_followers_box(self):
        try:
            close_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[5]/div/div/div[1]/div/div[2]/button'))
            )
            close_button.click()
        except Exception:
            pass
        print('\nLISTA FECHADA COM SUCESSO')

    def open_self_profile(self):
        try:
            profile_image = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[5]/span/img'))
            )
            profile_image.click()
        except:
            print('\nNão foi possível abrir o próprio perfil')

        try:
            profile = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[5]/div[2]/div[2]/div[2]/a[1]/div'))
            )
            profile.click()
        except:
            print('\nNão foi possível clicar no link do perfil')
        print('\nPERFIL ABERTO COM SUCESSO')

    def get_followers(self):
        self.open_followers()
        self.sweep_all_followers()
        try:
            followers_list_html = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[5]/div/div/div[2]/ul/div'))
            )      
            links = followers_list_html.find_elements_by_tag_name('a')
            self.followers = [name.text for name in links if name.text != '']
        except:
            print('\nErro ao capturar seguidores')
        self.close_followers_box()
        
        print('\nFunção get_followers executada com sucesso!')

    def get_following(self):
        self.open_following()
        self.sweep_all_followers()
        try:
            following_list_html = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[5]/div/div/div[2]/ul/div'))
            )
            links = following_list_html.find_elements_by_tag_name('a')
            self.following = [name.text for name in links if name.text != '']
        except:
            print('\nErro ao capturar lista de perfis seguidos')
        self.close_followers_box()
        print('\nFunção get_following executada com sucesso!')

    def get_unfollowers(self):
        self.unfollowers = [user for user in self.following if user not in self.followers]

    def farm_followers(self):
        print('\nComeçando a função farm_followers')
        try:
            self.open_self_profile(); sleep(2)
            for i in self.profile_list:
                self.search_profile(); sleep(2)
                self.open_followers(); sleep(2)
                self.sweep_followers(); sleep(2)
                self.follow(); sleep(2)
                self.close_followers_box(); sleep(2)
        except:
            print('\nErro na função farm_followers')
        
    def unfollow(self):
        self.open_self_profile(); sleep(2)
        self.open_following(); sleep(2)
        self.sweep_all_followers(); sleep(2)
        try:
            following_list_html = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[5]/div/div/div[2]/ul/div'))
            )      
            list_html = following_list_html.find_elements_by_tag_name('li')
            count = 0

            for l in list_html:
                following_profile = l.find_elements_by_tag_name('a')
                following_button = l.find_element_by_tag_name('button')
                for f in following_profile:
                    if f.text in self.unfollowers:
                        following_button.click()
                        count+=1
                        unfollow_button = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '/html/body/div[6]/div/div/div/div[3]/button[1]'))
                        )
                        sleep(2)
                        unfollow_button.click()
                        print('\nRemovido o follow do perfil:')
                        print(f.text)
                        print('Número de follows removidos:')
                        print(count)
                        print('Unfollowers restantes:')
                        self.unfollowers.remove(f.text)
                        print(len(self.unfollowers))
                        sleep(45)

            self.close_followers_box()
        except:
            print('\nErro na função unfollow')
            self.close_followers_box()
            pass

    def unfollow_unfollowers(self):
        try:
            self.open_self_profile(); sleep(2)

            self.get_followers()
            print('\n\nNúmero de Seguidores:')
            print(len(self.followers))

            self.get_following()
            print('\n\nNúmero de Seguindo:')
            print(len(self.following))

            unfollowers_lenght = len(self.unfollowers)
            while unfollowers_lenght>0:
                self.get_unfollowers()
                print('\nNúmero de perfis que não seguem de volta')
                print(len(self.unfollowers))

                self.unfollow()
            
        except:
            print('\nErro na função unfollow_unfollowers')

InstaBot()
