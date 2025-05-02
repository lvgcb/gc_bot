import json
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# States for conversation handlers
MENU, ADD_STUDENT, STUDENT_NAME, STUDENT_SURNAME, STUDENT_AGE, STUDENT_SCHOOL, STUDENT_TARIFF, STUDENT_MENTOR, STUDENT_PHONE, STUDENT_TELEGRAM, STUDENT_PARENT_NAME, STUDENT_PARENT_PHONE, CONFIRM_ADD, SEARCH_STUDENT, UPDATE_STATUS, DELETE_STUDENT = range(16)

# Database file path
DB_FILE = 'students_database.json'

# Initialize database if it doesn't exist
def initialize_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as file:
            json.dump({"students": []}, file)

# Load database
def load_database():
    try:
        with open(DB_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"students": []}

# Save database
def save_database(data):
    with open(DB_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Check if user is a mentor (you might want to implement a more robust authentication system)
async def is_mentor(update):
    # For now, we'll just check if the user is in a predefined list
    # In a real application, you'd want a more secure authentication system
    mentor_ids = [123456789]  # Replace with actual mentor IDs
    return update.effective_user.id in mentor_ids

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user is a mentor - temporarily disabled for testing
    # if not await is_mentor(update):
    #     await update.message.reply_text("Sorry, only mentors can use this bot.")
    #     return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("Add Student", callback_data="add_student")],
        [InlineKeyboardButton("Search Student", callback_data="search_student")],
        [InlineKeyboardButton("Update Student Status", callback_data="update_status")],
        [InlineKeyboardButton("Delete Student", callback_data="delete_student")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to the Education Center Management Bot!\n"
        "Please select an action:",
        reply_markup=reply_markup
    )
    return MENU

# Handle menu selection
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_student":
        await query.message.reply_text("Let's add a new student. What is the student's first name?")
        return STUDENT_NAME
    elif query.data == "search_student":
        await query.message.reply_text("Please enter the student's name or ID to search:")
        return SEARCH_STUDENT
    elif query.data == "update_status":
        await query.message.reply_text("Please enter the student's name or ID to update their status:")
        return UPDATE_STATUS
    elif query.data == "delete_student":
        await query.message.reply_text("Please enter the student's name or ID to delete:")
        return DELETE_STUDENT
    else:
        return MENU

# Adding student handlers
async def add_student_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student'] = {}
    context.user_data['student']['name'] = update.message.text
    await update.message.reply_text("Great! Now, what is the student's surname?")
    return STUDENT_SURNAME

async def add_student_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['surname'] = update.message.text
    await update.message.reply_text("How old is the student?")
    return STUDENT_AGE

async def add_student_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text)
        context.user_data['student']['age'] = age
        await update.message.reply_text("Which school does the student attend?")
        return STUDENT_SCHOOL
    except ValueError:
        await update.message.reply_text("Please enter a valid age (numbers only).")
        return STUDENT_AGE

async def add_student_school(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['school'] = update.message.text
    await update.message.reply_text("What tariff is the student on?")
    return STUDENT_TARIFF

async def add_student_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['tariff'] = update.message.text
    await update.message.reply_text("Who is the student's mentor?")
    return STUDENT_MENTOR

async def add_student_mentor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['mentor'] = update.message.text
    await update.message.reply_text("What is the student's phone number?")
    return STUDENT_PHONE

async def add_student_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['phone'] = update.message.text
    await update.message.reply_text("What is the student's Telegram ID? (If none, type 'None')")
    return STUDENT_TELEGRAM

async def add_student_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['telegram_id'] = update.message.text
    await update.message.reply_text("What is the parent's name?")
    return STUDENT_PARENT_NAME

async def add_student_parent_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['parent_name'] = update.message.text
    await update.message.reply_text("What is the parent's phone number?")
    return STUDENT_PARENT_PHONE

async def add_student_parent_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['student']['parent_phone'] = update.message.text
    
    # Generate a unique ID for the student
    data = load_database()
    new_id = len(data['students']) + 1
    context.user_data['student']['id'] = new_id
    context.user_data['student']['status'] = "Active"  # Default status
    
    # Display confirmation
    student = context.user_data['student']
    confirmation_text = f"""
Please confirm the student details:
ID: {student['id']}
Name: {student['name']} {student['surname']}
Age: {student['age']}
School: {student['school']}
Tariff: {student['tariff']}
Mentor: {student['mentor']}
Phone: {student['phone']}
Telegram ID: {student['telegram_id']}
Parent Name: {student['parent_name']}
Parent Phone: {student['parent_phone']}
Status: {student['status']}
"""
    
    keyboard = [
        [InlineKeyboardButton("Confirm", callback_data="confirm_add")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_add")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(confirmation_text, reply_markup=reply_markup)
    return CONFIRM_ADD

async def confirm_add_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_add":
        # Save student to database
        data = load_database()
        data['students'].append(context.user_data['student'])
        save_database(data)
        
        await query.message.reply_text("Student added successfully!")
        
        # Return to main menu
        keyboard = [
            [InlineKeyboardButton("Add Another Student", callback_data="add_student")],
            [InlineKeyboardButton("Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("What would you like to do next?", reply_markup=reply_markup)
        return MENU
    else:
        await query.message.reply_text("Student addition cancelled.")
        return await start(update, context)

# Search student handler
async def search_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_term = update.message.text.lower()
    data = load_database()
    found_students = []
    
    for student in data['students']:
        # Search by name, surname, or ID
        if (search_term in student['name'].lower() or 
            search_term in student['surname'].lower() or 
            search_term == str(student['id'])):
            found_students.append(student)
    
    if not found_students:
        await update.message.reply_text("No students found with that name or ID.")
    else:
        for student in found_students:
            student_info = f"""
ID: {student['id']}
Name: {student['name']} {student['surname']}
Age: {student['age']}
School: {student['school']}
Tariff: {student['tariff']}
Mentor: {student['mentor']}
Phone: {student['phone']}
Telegram ID: {student['telegram_id']}
Parent Name: {student['parent_name']}
Parent Phone: {student['parent_phone']}
Status: {student['status']}
"""
            await update.message.reply_text(student_info)
    
    # Return to main menu
    return await start(update, context)

# Update student status handler
async def update_status_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_term = update.message.text.lower()
    data = load_database()
    found_students = []
    
    for student in data['students']:
        if (search_term in student['name'].lower() or 
            search_term in student['surname'].lower() or 
            search_term == str(student['id'])):
            found_students.append(student)
    
    if not found_students:
        await update.message.reply_text("No students found with that name or ID.")
        return await start(update, context)
    
    context.user_data['found_students'] = found_students
    
    # If only one student found, offer status options
    if len(found_students) == 1:
        student = found_students[0]
        context.user_data['selected_student_id'] = student['id']
        
        keyboard = [
            [InlineKeyboardButton("Active", callback_data="status_active")],
            [InlineKeyboardButton("Inactive", callback_data="status_inactive")],
            [InlineKeyboardButton("On Hold", callback_data="status_onhold")],
            [InlineKeyboardButton("Graduated", callback_data="status_graduated")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Current status for {student['name']} {student['surname']}: {student['status']}\n"
            "Select new status:",
            reply_markup=reply_markup
        )
    else:
        # Multiple students found, let user select
        keyboard = []
        for student in found_students:
            button = InlineKeyboardButton(
                f"{student['name']} {student['surname']} (ID: {student['id']})",
                callback_data=f"select_{student['id']}"
            )
            keyboard.append([button])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Multiple students found. Please select one:", reply_markup=reply_markup)
    
    return UPDATE_STATUS

async def update_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("select_"):
        # User selected a student from list
        student_id = int(query.data.split("_")[1])
        context.user_data['selected_student_id'] = student_id
        
        # Find the selected student
        selected_student = None
        for student in context.user_data['found_students']:
            if student['id'] == student_id:
                selected_student = student
                break
        
        if selected_student:
            keyboard = [
                [InlineKeyboardButton("Active", callback_data="status_active")],
                [InlineKeyboardButton("Inactive", callback_data="status_inactive")],
                [InlineKeyboardButton("On Hold", callback_data="status_onhold")],
                [InlineKeyboardButton("Graduated", callback_data="status_graduated")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                f"Current status for {selected_student['name']} {selected_student['surname']}: {selected_student['status']}\n"
                "Select new status:",
                reply_markup=reply_markup
            )
    
    elif query.data.startswith("status_"):
        # User selected a status
        new_status = query.data.split("_")[1].capitalize()
        student_id = context.user_data['selected_student_id']
        
        # Update the student's status in the database
        data = load_database()
        for student in data['students']:
            if student['id'] == student_id:
                student['status'] = new_status
                break
        
        save_database(data)
        
        await query.message.reply_text(f"Status updated to {new_status} successfully!")
        return await start(update, context)
    
    return UPDATE_STATUS

# Delete student handler
async def delete_student_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_term = update.message.text.lower()
    data = load_database()
    found_students = []
    
    for student in data['students']:
        if (search_term in student['name'].lower() or 
            search_term in student['surname'].lower() or 
            search_term == str(student['id'])):
            found_students.append(student)
    
    if not found_students:
        await update.message.reply_text("No students found with that name or ID.")
        return await start(update, context)
    
    context.user_data['found_students'] = found_students
    
    # If only one student found, confirm deletion
    if len(found_students) == 1:
        student = found_students[0]
        context.user_data['selected_student_id'] = student['id']
        
        keyboard = [
            [InlineKeyboardButton("Yes, delete this student", callback_data="confirm_delete")],
            [InlineKeyboardButton("No, cancel", callback_data="cancel_delete")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Are you sure you want to delete {student['name']} {student['surname']} (ID: {student['id']})?",
            reply_markup=reply_markup
        )
    else:
        # Multiple students found, let user select
        keyboard = []
        for student in found_students:
            button = InlineKeyboardButton(
                f"{student['name']} {student['surname']} (ID: {student['id']})",
                callback_data=f"select_delete_{student['id']}"
            )
            keyboard.append([button])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Multiple students found. Please select one to delete:", reply_markup=reply_markup)
    
    return DELETE_STUDENT

async def delete_student_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("select_delete_"):
        # User selected a student from list
        student_id = int(query.data.split("_")[2])
        context.user_data['selected_student_id'] = student_id
        
        # Find the selected student
        selected_student = None
        for student in context.user_data['found_students']:
            if student['id'] == student_id:
                selected_student = student
                break
        
        if selected_student:
            keyboard = [
                [InlineKeyboardButton("Yes, delete this student", callback_data="confirm_delete")],
                [InlineKeyboardButton("No, cancel", callback_data="cancel_delete")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                f"Are you sure you want to delete {selected_student['name']} {selected_student['surname']} (ID: {selected_student['id']})?",
                reply_markup=reply_markup
            )
    
    elif query.data == "confirm_delete":
        # User confirmed deletion
        student_id = context.user_data['selected_student_id']
        
        # Remove the student from the database
        data = load_database()
        data['students'] = [student for student in data['students'] if student['id'] != student_id]
        save_database(data)
        
        await query.message.reply_text("Student deleted successfully!")
        return await start(update, context)
    
    elif query.data == "cancel_delete":
        await query.message.reply_text("Deletion cancelled.")
        return await start(update, context)
    
    return DELETE_STUDENT

# Main function
def main():
    # Initialize database
    initialize_db()
    
    # Set up application with your token
    application = ApplicationBuilder().token("7997238330:AAH4iCiYOmAHoKzjmvXn13AlMSnif6oJIUE").build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [CallbackQueryHandler(menu_handler)],
            
            # Add student states
            STUDENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_name)],
            STUDENT_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_surname)],
            STUDENT_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_age)],
            STUDENT_SCHOOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_school)],
            STUDENT_TARIFF: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_tariff)],
            STUDENT_MENTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_mentor)],
            STUDENT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_phone)],
            STUDENT_TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_telegram)],
            STUDENT_PARENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_parent_name)],
            STUDENT_PARENT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_parent_phone)],
            CONFIRM_ADD: [CallbackQueryHandler(confirm_add_student)],
            
            # Search student state
            SEARCH_STUDENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_student)],
            
            # Update status states
            UPDATE_STATUS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, update_status_search),
                CallbackQueryHandler(update_status_handler)
            ],
            
            # Delete student states
            DELETE_STUDENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_student_search),
                CallbackQueryHandler(delete_student_handler)
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    application.add_handler(conv_handler)
    
    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
