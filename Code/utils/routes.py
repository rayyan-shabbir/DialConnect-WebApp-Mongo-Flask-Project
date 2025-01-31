from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from .controller import Controller
import re
from .config import SECRET_KEY, MONGO_HOST, MONGO_PORT
from .common_data import USER_STATUS, ADMIN_EMAIL, ADMIN_PASSWORD, COMMON_FIELDS


# Initialize the Flask application
app = Flask(__name__)
app.secret_key = SECRET_KEY # Set the secret key for session management if required in future


# Define the FlaskApp FlaskApp class to handle routing
class FlaskApp:
    """
    A class to handle routing and business logic for the Flask application.
    """

    # Composing the Controller instance
    def __init__(self):
        """
        Initialize the FlaskApp class with an instance of the Controller.
        """
        self.controller = Controller()


    # Method to add URL rules to the Flask App
    def route_handler(self, rule, endpoint, view_func, methods=None):
        """
        Add URL rules to the Flask application.

        :param rule: The URL rule as a string.
        :param endpoint: The endpoint for the registered URL rule.
        :param view_func: The function to call when serving a request to the provided endpoint.
        :param methods: The list of HTTP methods allowed for the rule.
        """
        if methods is None:
            # Default GET method if not specified 
            methods = ['GET']
        app.add_url_rule(rule, endpoint, view_func, methods=methods)

    # Route for the web home page
    def web_home(self):
        """
        Render the web home page.

        :return: The rendered web home template.
        """
        return render_template('web_home.html')

    # Route the user signup
    def signup(self):
        """
        Handle user signup.

        :return: Redirect to the signup page or render the signup template.
        """
        if request.method == 'POST':
            name = request.form['name'].strip()
            email = request.form['email'].strip()
            password = request.form['password'].strip()
            organization = request.form.get('organization', '').strip()
            designation = request.form['designation'].strip()

            # Validate required credentials
            if not all([name, email, password, designation]):
                flash('All fields except organization are required.', 'Warning!')
                return redirect(url_for('signup'))

            # Check if email is already registered to redirect again to signup
            if self.controller.is_email_registered(email):
                flash('Email already registered, please login instead.', 'Warning!')
                return redirect(url_for('signup'))

            # Error Handling
            try:
                # Registering the user
                self.controller.register_user(name, email, password, organization, designation)
                flash('Signup successful!', 'success')
                return redirect(url_for('signup'))
            except Exception as e:
                flash(f"An error occurred: {str(e)}", 'Warning!')
                return redirect(url_for('signup'))

        # Render the signup template
        return render_template('signup.html')

    # Route the user login
    def login(self):
        """
        Handle user login.

        :return: Redirect to the login page or render the login template.
        """
        if request.method == 'POST':
            email = request.form['email'].strip()
            password = request.form['password'].strip()

            # Validate email and password
            if not email or not password:
                flash('Both email and password are required.', 'danger')
                return redirect(url_for('login'))

            # Check for admin login
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                session['admin_id'] = "123098"
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_table'))

            # Validate user credentials
            user = self.controller.validate_user(email, password)
            if user:
                session['user_id'] = str(user['_id'])
                return redirect(url_for('user_home'))
            else:
                flash('Invalid email or password.', 'danger')
                return redirect(url_for('login'))

        # Render the login template
        return render_template('login.html')

    # Route for user logout
    def logout(self):
        """
        Handle user logout.

        :return: Redirect to the login page.
        """
        # Remove user ID & admin ID from session
        session.pop('user_id', None)
        session.pop('admin_id', None)
        session.clear()
        flash('You have been logged out.', 'success')
        response = redirect(url_for('login'))
        response.headers['Cache-Control'] = 'no-store'
        return response

    # Route for user home page
    def user_home(self):
        """
        Render the user home page.

        :return: Redirect to the login page or render the user home template.
        """
        if 'user_id' in session:
            user = self.controller.get_user_by_id(session['user_id'])
            if user:
                user_name = user.get('name', 'User')
                team_name = user.get('organization', 'Not Assigned')
                designation = user.get('designation', 'Not Available')
                user_email = user.get('email', 'Not Available')
                return render_template('user_home.html', user_name=user_name, team_name=team_name, designation=designation, user_email=user_email)
            else:
                flash('User not found.', 'Warning!')
                return redirect(url_for('login'))
        else:
            flash('Please login first.', 'Warning!')
            return redirect(url_for('login'))

    # Route for user connect (adding dial plans)
    def user_connect(self):
        """
        Handle user connect (adding dial plans).

        :return: Redirect to the login page or render the user connect template.
        """
        if 'user_id' not in session:
            flash('Please login to access this page.', 'Warning!')
            return redirect(url_for('login'))

        if request.method == 'POST':
            # Error Handling
            try:
                insurance_company = request.form.get('insurance_company').strip()
                form_data = []
                actions_data = {}
                json_data = {}
                fields_list = [] 
                counter = 1
                flag = False

                # Check if insurance company already exists
                if self.controller.check_insurance_exists(insurance_company):
                    print(self.controller.check_insurance_exists(insurance_company))
                    # print("COME HERE") 
                    return jsonify({'success': False, 'error': 'Insurance company already exists.'}), 400

                while True:
                    # Getting form data from frontend
                    field = request.form.get(f'field_{counter}')
                    sentence = request.form.get(f'sentence_{counter}')
                    action = request.form.get(f'action_{counter}')
                    callback = request.form.get(f'callback_{counter}')
                    custom_field = request.form.get(f'custom_field_{counter}', '').strip()
                    is_custom_field = False
                    

                    action_callback = ""

                    # Converting callback to required format for backend
                    if callback and callback == "Keypad":
                        action_callback = "send_dtmf"
                    elif callback and callback == "Audio":
                        action_callback = "send_audio_words"

                    if not field:
                        field = custom_field
                        is_custom_field = True

                    if field and sentence:
                        # Converting the insurance company name to specified format
                        formatted_company = re.sub(r'\s+', '_', insurance_company)
                        formatted_custom_field = re.sub(r'\s+', '_', custom_field)
                        formatted_field = f"{formatted_company}_{formatted_custom_field}" if is_custom_field else re.sub(r'\s+', '_', field)

                        action_value = action if is_custom_field else ""
                        # In case of DOB & DOS the indices are hard coded.
                        indices_value = [[5, 7], [8, 10], [0, 4]] if field.lower() in ['dob', 'dos'] else []

                        # Adding sentence to sentence collection
                        self.controller.add_sentence(formatted_field, sentence)

                        form_data.append({
                            'field': formatted_field,
                            'sentence': sentence,
                            'action': action_value,
                            'callback': callback
                        })

                        fields_list.append(formatted_field)  # Add field to the list

                        key1 = ""
                        if field in COMMON_FIELDS:
                            key1 = field

                        actions_data[formatted_field] = {
                            "excel": {
                                "key": key1,
                                "indices": indices_value,
                                "regex": []
                            },
                            "sending_data": action_value,
                            "callback": action_callback or ""
                        }

                        if insurance_company not in json_data:
                            json_data[insurance_company] = {}
                            json_data["uuid"] = session['user_id']

                        json_data[insurance_company][formatted_field] = {
                            "sentence": sentence,
                            "action": action if action else "",
                            "callback": callback if callback else ""
                        }

                        counter += 1
                    else:
                        break
                    

                if not form_data:
                    # If no data is provided, insert an empty JSON object for the insurance company
                    json_data[insurance_company] = {}
                    json_data["uuid"] = session['user_id']


                if actions_data:
                    self.controller.update_actions(insurance_company, actions_data)


                if json_data:
                    self.controller.insert_individual(json_data)
                    

                
                # Update insurance with the list of fields
                self.controller.update_insurance(insurance_company, fields_list)


                return jsonify({'success': True}), 200

            except Exception as e:
                print(f"Error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

         # Render the user connect template
        return render_template('user_connect.html')

    # Route for user table (list of insurances)
    def user_table(self):
        """
        Render the user table (list of insurances).

        :return: Redirect to the login page or render the user table template.
        """
        # Session verification
        if 'user_id' not in session:
            flash('Please login to access this page.', 'Warning!')
            return redirect(url_for('login'))

        insurance_docs = self.controller.get_individual_collection_by_uuid(session['user_id'])
        insurances = []
        for doc in insurance_docs:
            insurances.append(list(doc.keys())[1])

        # Render the user table template
        return render_template('user_table.html', insurances=insurances)

    # Route for editing insurance details
    def edit_insurance(self, insurance_name):
        """
        Handle editing insurance details.

        :param insurance_name: The name of the insurance company.
        :return: Redirect to the login page or render the edit insurance template.
        """
        if request.method == 'POST':
            updated_fields = {}
            counter = 1
            while True:
                # Getting form data from frontend
                field = request.form.get(f'field_{counter}')
                sentence = request.form.get(f'sentence_{counter}')
                action = request.form.get(f'action_{counter}')
                callback = request.form.get(f'callback_{counter}')

                if field == "other":
                    # Convert the insurance company name to specified format
                    field = request.form.get(f'custom_field_{counter}')
                    formatted_company = re.sub(r'\s+', '_', insurance_name)
                    formatted_custom_field = re.sub(r'\s+', '_', field)
                    formatted_field = f"{formatted_company}_{formatted_custom_field}"
                    field = formatted_field

                # In case of DOB & DOS the indices are hard coded.
                indices_value = [[5, 7], [8, 10], [0, 4]] if field and field.lower() in ['dob', 'dos'] else []

                key = ""
                if field in COMMON_FIELDS:
                    key = field

                if field and sentence:
                    updated_fields[field] = {
                        "sentence": sentence,
                        "action": action if action else "",
                        "callback": callback if callback else "",
                        "key": key if key else "",
                        "indices_value": indices_value if indices_value else ""
                    }
                    counter += 1
                else:
                    break

            self.controller.update_individual(insurance_name, updated_fields)

            # Update the insurances collection to reflect the changes
            insurance_doc = self.controller.get_individual_collection_by_name(insurance_name)
            if insurance_doc:
                current_fields = set(insurance_doc[insurance_name].keys())
                updated_fields_set = set(updated_fields.keys())

                # Fields to remove
                fields_to_remove = current_fields - updated_fields_set

                # Remove fields from the insurances collection
                for field in fields_to_remove:
                    self.controller.remove_field_from_insurance(insurance_name, field)

            fields_list = list(updated_fields.keys())
            self.controller.update_insurance(insurance_name, fields_list)

            actions_data = {}
            for field, details in updated_fields.items():
                action_callback = ""

                if details["callback"] and details["callback"] == "Keypad":
                    action_callback = "send_dtmf"
                elif details["callback"] and details["callback"] == "Audio":
                    action_callback = "send_audio_words"

                actions_data[field] = {
                    "excel": {"key": details["key"], "indices": details["indices_value"], "regex": []},
                    "sending_data": details["action"],
                    "callback": action_callback
                }
            self.controller.update_actions(insurance_name, actions_data)

            for field, details in updated_fields.items():
                # Check if the sentence already exists before adding
                existing_sentences = self.controller.sentences_collection.find_one({"_id": "default"})
                if existing_sentences and field in existing_sentences:
                    if details["sentence"] not in existing_sentences[field]:
                        self.controller.add_sentence(field, details["sentence"])
                else:
                    self.controller.add_sentence(field, details["sentence"])

            # Remove duplicates in the sentences collection
            self.controller.sentences_collection.remove_duplicates()

            flash('Insurance updated successfully', 'success')
            if "admin_id" in session:
                return redirect(url_for('admin_table'))
            else:
                return redirect(url_for('user_table'))

        insurance_doc = self.controller.get_individual_collection_by_name(insurance_name)
        if not insurance_doc:
            flash('Insurance not found', 'danger')
            return redirect(url_for('user_table'))

        fields_data = insurance_doc[insurance_name]

        if 'admin_id' in session:
            return render_template('edit_insurance.html', insurance_name=insurance_name, fields_data=fields_data, key="admin")
        else:
            return render_template('edit_insurance.html', insurance_name=insurance_name, fields_data=fields_data, key="user")


    # Route for deleting insurance
    def delete_insurance(self, insurance_name):
        """
        Handle deleting insurance.

        :param insurance_name: The name of the insurance company.
        :return: Redirect to the login page or render the user table template.
        """
        # # Session Handling
        # if 'user_id' and 'admin_id' not in session:
        #     flash('Please login to access this page.', 'Warning!')
        #     return redirect(url_for('login'))

        self.controller.delete_individual(insurance_name)

        self.controller.delete_insurance(insurance_name)

        self.controller.delete_actions(insurance_name)

        if 'user_id' in session:
            flash('Insurance deleted successfully', 'success')
            return redirect(url_for('user_table'))
        elif 'admin_id' in session:
            flash('Insurance deleted successfully', 'success')
            return redirect(url_for('admin_table'))

    # Route for showing insurance details
    def show_insurance(self, insurance_name):
        """
        Render the insurance details page.

        :param insurance_name: The name of the insurance company.
        :return: Redirect to the login page or render the show insurance template.
        """
        # # Session Handling
        # if 'user_id' and 'admin_id' not in session:
        #     flash('Please login to access this page.', 'Warning!')
        #     return redirect(url_for('login'))

        insurance_doc = self.controller.get_individual_collection_by_name(insurance_name)
        if not insurance_doc:
            flash('Insurance not found', 'danger') 
            return redirect(url_for('user_table'))

        fields_data = insurance_doc[insurance_name]

        if 'admin_id' in session:
            return render_template('show_insurance.html', insurance_name=insurance_name, fields_data=fields_data, key="admin")
        else:
            return render_template('show_insurance.html', insurance_name=insurance_name, fields_data=fields_data, key="user")

    # Route for admin table (list of insurances)
    def admin_table(self):
        """
        Render the admin table (list of insurances).

        :return: Redirect to the login page or render the admin table template.
        """
        if 'admin_id' not in session:
            flash('Please login to access this page.', 'Warning!')
            return redirect(url_for('login'))

        insurance_docs = self.controller.get_all_individual_collections()
        insurances = []
        for doc in insurance_docs:
            insurances.append(list(doc.keys())[1])

        return render_template('admin_table.html', insurances=insurances)

    def admin_graphs(self):
        """
        Render the admin graphs page.

        :return: Redirect to the login page or render the admin graphs template.
        """
        if 'admin_id' not in session:
            flash('Please login to access this page.', 'Warning!')
            return redirect(url_for('login'))

        callbacks = self.controller.get_callback_distribution()
        # Render the admin graphs template
        return render_template('admin_graphs.html', callbacks=callbacks)


# Create an instance of the FlaskApp class
route_instance = FlaskApp()

# Register routes
route_instance.route_handler('/', 'web_home', route_instance.web_home)
route_instance.route_handler('/signup', 'signup', route_instance.signup, methods=['GET', 'POST'])
route_instance.route_handler('/login', 'login', route_instance.login, methods=['GET', 'POST'])
route_instance.route_handler('/logout', 'logout', route_instance.logout)
route_instance.route_handler('/user_home', 'user_home', route_instance.user_home)
route_instance.route_handler('/user_connect', 'user_connect', route_instance.user_connect, methods=['GET', 'POST'])
route_instance.route_handler('/user_table', 'user_table', route_instance.user_table)
route_instance.route_handler('/edit_insurance/<insurance_name>', 'edit_insurance', route_instance.edit_insurance, methods=['GET', 'POST'])
route_instance.route_handler('/delete_insurance/<insurance_name>', 'delete_insurance', route_instance.delete_insurance)
route_instance.route_handler('/show_insurance/<insurance_name>', 'show_insurance', route_instance.show_insurance)
route_instance.route_handler('/admin_table', 'admin_table', route_instance.admin_table)
route_instance.route_handler('/admin_graphs', 'admin_graphs', route_instance.admin_graphs)


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)