import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from models import setup_db, Question, Category
from flask_cors import CORS
import random

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,selection):
    page = request.args.get('page',1, type=int)
    start=(page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions= [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions
def decorate_categories(categories):
    decorated={}
    for cat in categories:
        decorated[str(cat.id)]=cat.type
    return decorated


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)  # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs



  # @TODO: Use the after_request decorator to set Access-Control-Allow

  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      return response

  # @TODO:
  # Create an endpoint to handle GET requests
  # for all available categories.
  @app.route('/categories')
  def get_categories():
      # categories=Category.query.all()
      categories=decorate_categories(Category.query.all())

      if len(categories) == 0 :
          abort(404)
      return jsonify({
      'success': True,
      'categories': categories,
      'total_categories': len(categories),
      })

  # @TODO:
  # Create an endpoint to handle GET requests for questions,
  # including pagination (every 10 questions).
  # This endpoint should return a list of questions,
  # number of total questions, current category, categories.
  #
  # TEST: At this point, when you start the application
  # you should see questions and categories generated,
  # ten questions per page and pagination at the bottom of the screen for three pages.
  # Clicking on the page numbers should update the questions.
  @app.route('/questions')
  def get_questions():
      selection=Question.query.all()
      # categories=[cat.format() for cat in Category.query.all()]
      categories=decorate_categories(Category.query.all())
      current_questions=paginate_questions(request,selection)
      if len(current_questions) == 0 :
          abort(404)
      return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': categories,
      'current_category':'All'
      })

  # @TODO:
  # Create an endpoint to DELETE question using a question ID.
  #
  # TEST: When you click the trash icon next to a question, the question will be removed.
  # This removal will persist in the database and when you refresh the page.
  @app.route('/questions/<id>', methods=['DELETE'])
  def delete_question(id):
      try:
         question= Question.query.filter(Question.id == id).one_or_none()
         if question is None:
              abort(404)
         question.delete()
         selection = Question.query.order_by(Question.id).all()
         current_questions=paginate_questions(request,selection)

         return jsonify({
          'success': True,
          'deleted':question.id,
          'questions': current_questions,
          'total_questions': len(Question.query.all())
         })
      except:
          abort(422)


  # @TODO:
  # Create an endpoint to POST a new question,
  # which will require the question and answer text,
  # category, and difficulty score.
  #
  # TEST: When you submit a question on the "Add" tab,
  # the form will clear and the question will appear at the end of the last page
  # of the questions list in the "List" tab.

  # @TODO:
  # Create a POST endpoint to get questions based on a search term.
  # It should return any questions for whom the search term
  # is a substring of the question.
  #
  # TEST: Search by any phrase. The questions list will update to include
  # only question that include that string within their question.
  # Try using the word "title" to start.

  @app.route('/questions', methods=['POST'])
  def create_question():
      body = request.get_json()
      new_question =body.get('question',None)
      new_answer =body.get('answer',None)
      new_difficulty =body.get('difficulty',None)
      new_category =body.get('category',None)
      search = body.get('searchTerm',None)
      try:
          if search:
              selection= Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
              current_question = paginate_questions(request,selection)
              return jsonify({
              'success': True,
              'questions':current_question,
              'current_category':'All',
              'total_questions':len(selection.all())
              })
          else:
              if not new_question or not new_answer:
                  abort(422)
              question=Question(question=new_question, answer=new_answer, difficulty = new_difficulty, category = new_category)
              question.insert()

              return jsonify({
              'success':True,
              'created':question.id
              })
      except:
          abort(422)


  # @TODO:
  # Create a GET endpoint to get questions based on category.
  #
  # TEST: In the "List" tab / main screen, clicking on one of the
  # categories in the left column will cause only questions of that
  # category to be shown.

  @app.route('/categories/<int:category_id>/questions')
  def get_by_category(category_id):
      try:
          selection=Question.query.join(Category,Question.category == Category.id).filter(Question.category == category_id).all()
          # categories=[cat.format() for cat in Category.query.all()]
          categories=decorate_categories(Category.query.all())
          current_questions=paginate_questions(request,selection)
          if len(current_questions) == 0 :
              abort(404)
          return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection),
          'categories': categories,
          'current_category':category_id
          })

      except:
          abort(422)
  # @TODO:
  # Create a POST endpoint to get questions to play the quiz.
  # This endpoint should take category and previous question parameters
  # and return a random questions within the given category,
  # if provided, and that is not one of the previous questions.
  #
  # TEST: In the "Play" tab, after a user selects "All" or a category,
  # one question at a time is displayed, the user is allowed to answer
  # and shown whether they were correct or not.
  @app.route('/quizzes', methods=['POST'])#/<int:cat_id>
  def show_quizzes():#cat_id
        body = request.get_json()
        category =body.get('quiz_category',None)

        previous_questions =body.get('previous_questions',None)
        if not previous_questions :
            previous_questions=[]
        if category:
            random_question=Question.query.filter(Question.id.notin_(previous_questions),Question.category == category).order_by(func.random()).first()
        else:
            random_question=Question.query.filter(Question.id.notin_(previous_questions)).order_by(func.random()).first()
        if (random_question) is None :
            return jsonify({
            'success': True,
            'message': 'No available Question'})

        return jsonify({
            'success': True,
            'question': random_question.format(),
            })
  # @TODO:
  # Create error handlers for all expected errors
  # including 404 and 422.
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
      }), 422
  return app
