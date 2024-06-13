import streamlit as st
import streamlit_authenticator as stauth
from dependancies import sign_up, fetch_users
import streamlit as st
import machine_learning as ml
import feature_extraction as fe
from bs4 import BeautifulSoup
import requests as re
import matplotlib.pyplot as plt


st.set_page_config(page_title='Streamlit', page_icon='🐍',
                   initial_sidebar_state='collapsed')
st.title(
    'ThroneGuard: Defending Against Phishing Dragons - A Machine Learning Approach')

try:
    users = fetch_users()
    emails = []
    usernames = []
    passwords = []

    for user in users:
        emails.append(user['key'])
        usernames.append(user['username'])
        passwords.append(user['password'])

    credentials = {'usernames': {}}
    for index in range(len(emails)):
        credentials['usernames'][usernames[index]] = {
            'name': emails[index], 'password': passwords[index]}

    Authenticator = stauth.Authenticate(
        credentials, cookie_name='Streamlit', key='abcdef', cookie_expiry_days=4)

    email, authentication_status, username = Authenticator.login(
        ':green[Login]', 'main')

    info, info1 = st.columns(2)

    if not authentication_status:
        sign_up()

    if username:
        if username in usernames:
            if authentication_status:
                # let User see app
                st.sidebar.subheader(f'Welcome {username}')
                Authenticator.logout('Log Out', 'sidebar')

                # st.title(
                #     'ThroneGuard: Defending Against Phishing Dragons - A Machine Learning Approach')
                st.write('This ML-based webpage is developed as our college Minor Project. Objective of the app is detecting phishing '
                         'websites only using content data. Not URL!'
                         ' You can see the details of approach, data set, and feature set if you click on _"See The Details"_. ')

                with st.expander("PROJECT DETAILS"):
                    st.subheader('Approach')
                    st.write('We used _supervised learning_ to classify phishing and legitimate websites. '
                             'We took the benefit from content-based approach and focused on html of the websites. '
                             'Also, We used scikit-learn for the ML models.'
                             )
                    st.write('For this educational project, '
                             'We created our own data set and defined features, some from the literature and some based on manual '
                             'analysis.'
                             ' We used requests library to collect data, BeautifulSoup module to parse and extract features. ')

                    st.subheader('Data set')
                    st.write(
                        'We used _"phishtank.org"_ & _"tranco-list.eu"_ as data sources.')
                    st.write(
                        'Totally 26584 websites ==> **_16060_ legitimate** websites | **_10524_ phishing** websites')
                    st.write('Data set was created in October 2024.')

                    # ----- FOR THE PIE CHART ----- #
                    labels = 'phishing', 'legitimate'
                    phishing_rate = int(
                        ml.phishing_df.shape[0] / (ml.phishing_df.shape[0] + ml.legitimate_df.shape[0]) * 100)
                    legitimate_rate = 100 - phishing_rate
                    sizes = [phishing_rate, legitimate_rate]
                    explode = (0.1, 0)
                    fig, ax = plt.subplots()
                    ax.pie(sizes, explode=explode, labels=labels,
                           shadow=True, startangle=90, autopct='%1.1f%%')
                    ax.axis('equal')
                    st.pyplot(fig)
                    # ----- !!!!! ----- #

                    st.write('Features + URL + Label ==> Dataframe')
                    st.markdown('label is 1 for phishing, 0 for legitimate')
                    number = st.slider("Select row number to display", 0, 100)
                    st.dataframe(ml.legitimate_df.head(number))

                    @st.cache_data
                    def convert_df(df):
                        # IMPORTANT: Cache the conversion to prevent computation on every rerun
                        return df.to_csv().encode('utf-8')

                    csv = convert_df(ml.df)

                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name='phishing_legitimate_structured_data.csv',
                        mime='text/csv',
                    )

                    st.subheader('Features')
                    st.write('We used only content-based features. We didn\'t use url-based faetures like length of url etc.'
                             'Most of the features extracted using find_all() method of BeautifulSoup module after parsing html.')

                    st.subheader('Results')
                    st.write('We used 7 different ML classifiers of scikit-learn and tested them implementing k-fold cross validation.'
                             'Firstly obtained their confusion matrices, then calculated their accuracy, precision and recall scores.'
                             'Comparison table is below:')
                    st.table(ml.df_results)
                    st.write('NB --> Gaussian Naive Bayes')
                    st.write('SVM --> Support Vector Machine')
                    st.write('DT --> Decision Tree')
                    st.write('RF --> Random Forest')
                    st.write('AB --> AdaBoost')
                    st.write('NN --> Neural Network')
                    st.write('KN --> K-Neighbours')

                with st.expander('EXAMPLE PHISHING URLs:'):
                    st.write('_https://banrural-02.web.app/_')
                    st.write('_https://karafuru.invite-mint.com/_')
                    st.write('_https://defi-ned.top/h5/#/_')
                    st.caption(
                        'REMEMBER, PHISHING WEB PAGES HAVE SHORT LIFECYCLE! SO, THE EXAMPLES SHOULD BE UPDATED!')

                choice = st.selectbox("Please select your machine learning model",
                                      [
                                          'Gaussian Naive Bayes', 'Support Vector Machine', 'Decision Tree', 'Random Forest',
                                          'AdaBoost', 'Neural Network', 'K-Neighbours'
                                      ]
                                      )

                model = ml.nb_model

                if choice == 'Gaussian Naive Bayes':
                    model = ml.nb_model
                    st.write('GNB model is selected!')
                elif choice == 'Support Vector Machine':
                    model = ml.svm_model
                    st.write('SVM model is selected!')
                elif choice == 'Decision Tree':
                    model = ml.dt_model
                    st.write('DT model is selected!')
                elif choice == 'Random Forest':
                    model = ml.rf_model
                    st.write('RF model is selected!')
                elif choice == 'AdaBoost':
                    model = ml.ab_model
                    st.write('AB model is selected!')
                elif choice == 'Neural Network':
                    model = ml.nn_model
                    st.write('NN model is selected!')
                else:
                    model = ml.kn_model
                    st.write('KN model is selected!')

                url = st.text_input('Enter the URL')
                # check the url is valid or not
                if st.button('Check!'):
                    try:
                        response = re.get(url, verify=False, timeout=4)
                        if response.status_code != 200:
                            print(
                                ". HTTP connection was not successful for the URL: ", url)
                        else:
                            soup = BeautifulSoup(
                                response.content, "html.parser")
                            # it should be 2d array, so I added []
                            vector = [fe.create_vector(soup)]
                            result = model.predict(vector)
                            if result[0] == 0:
                                st.success("This web page seems a legitimate!")
                                st.balloons()
                            else:
                                st.warning(
                                    "Attention! This web page is a potential PHISHING!")
                                st.snow()

                    except re.exceptions.RequestException as e:
                        print("--> ", e)

            elif not authentication_status:
                with info:
                    st.error('Incorrect Password or username')
            else:
                with info:
                    st.warning('Please feed in your credentials')
        else:
            with info:
                st.warning('Username does not exist, Please Sign up')


except:
    st.success('Refresh Page')
