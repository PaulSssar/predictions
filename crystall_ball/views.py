"""Views для страницы гадания."""
import random
import logging
from typing import cast
from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .forms import QuestionForm
from .models import Answer, Question, Cards
from .service import (
    create_reading,
    GigaChatBadResponse,
    GigaChatTimeout,
    GigaChatUnavailable,
)

logger = logging.getLogger(__name__)


@login_required
def crystal_ball(request):
    """View-функция для страницы вопроса.
    Передает форму при GET-запросе. При POST-запросе
    сохраняет вопрос и перенаправляет на страницу с ответом."""
    form = QuestionForm(request.POST or None)
    if form.is_valid():
        text = form.cleaned_data['text']
        user = request.user
        Question.objects.create(
            text=text,
            user=user,
        )
        return redirect('crystal_ball:answer', request.user.id)
    template = 'crystall_ball/question.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def answer(request, id):
    """View-функция для страницы ответа.
    Передает данные о всех вопросах пользователя,
    количестве аналогичных вопросов, список последних 10
    вопросов текущего пользователя и AI-трактовку расклада."""
    request_id = uuid4().hex

    all_questions = Question.objects.filter(user_id=request.user)[:10]
    current_question = Question.objects.filter(user_id=request.user).last()

    if not current_question:
        return redirect('crystal_ball:question')

    count_current_q = Question.objects.filter(text=current_question.text).count()

    if request.user.id != id:
        return redirect('crystal_ball:question')

    all_cards = Cards.objects.all()
    cards = random.sample(list(all_cards), 3)
    logger.info(
        "cards_drawn",
        extra={"request_id": request_id, "cards_count": len(cards)},
    )

    card_names = [card.name for card in cards]

    try:
        result = create_reading(
            card_names=card_names,
            question=current_question.text,
            request_id=request_id,
        )
    except GigaChatTimeout:
        logger.warning(
            "reading_timeout",
            extra={"request_id": request_id},
        )
        return render(
            request,
            'crystall_ball/answer.html',
            {
                'all_questions': all_questions,
                'question': current_question,
                'count_q': count_current_q,
                'cards': cards,
                'error': 'Не дождались ответа. Попробуйте позже.',
            },
            status=504,
        )
    except GigaChatUnavailable:
        logger.warning(
            "reading_unavailable",
            extra={"request_id": request_id},
        )
        return render(
            request,
            'crystall_ball/answer.html',
            {
                'all_questions': all_questions,
                'question': current_question,
                'count_q': count_current_q,
                'cards': cards,
                'error': 'Сейчас не получается заглянуть в карты. Попробуйте позже.',
            },
            status=503,
        )
    except GigaChatBadResponse:
        logger.warning(
            "reading_bad_response",
            extra={"request_id": request_id},
        )
        return render(
            request,
            'crystall_ball/answer.html',
            {
                'all_questions': all_questions,
                'question': current_question,
                'count_q': count_current_q,
                'cards': cards,
                'error': 'Сейчас не получается заглянуть в карты. Попробуйте позже.',
            },
            status=502,
        )

    # Сохранение ответа в базу данных
    answer_obj = Answer.objects.create(
        question=current_question,
        text=result.text,
    )

    logger.info(
        "reading_ok",
        extra={"request_id": request_id, "answer_length": len(result.text)},
    )

    context = {
        'all_questions': all_questions,
        'answer': answer_obj.text,
        'question': current_question,
        'count_q': count_current_q,
        'cards': cards,
    }
    return render(request, 'crystall_ball/answer.html', context)


@login_required
def all_questions(request, id):
    """Список всех вопросов текущего пользователя."""
    all_questions = Question.objects.filter(user=request.user)
    context = {
        'all_questions': all_questions,
    }
    template = 'crystall_ball/all_questions.html'
    return render(request, template, context)
