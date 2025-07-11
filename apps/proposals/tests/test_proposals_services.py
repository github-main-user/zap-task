from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from apps.proposals import services
from apps.proposals.models import Proposal

User = get_user_model()


@pytest.mark.django_db
@patch("apps.proposals.services.send_email_notification.delay")
def test_accept_proposal(mock_send_email_notification, user_factory, proposal_factory):
    freelancer1 = user_factory(email="f1@f1.com", role=User.UserRole.FREELANCER)
    freelancer2 = user_factory(email="f2@f2.com", role=User.UserRole.FREELANCER)

    proposal = proposal_factory(freelancer=freelancer1)
    other_proposal = proposal_factory(task=proposal.task, freelancer=freelancer2)

    services.accept_proposal(proposal)

    proposal.refresh_from_db()
    other_proposal.refresh_from_db()
    proposal.task.refresh_from_db()

    assert proposal.status == Proposal.ProposalStatus.ACCEPTED
    assert proposal.task.freelancer == proposal.freelancer
    assert other_proposal.status == Proposal.ProposalStatus.REJECTED
    assert mock_send_email_notification.call_count == 2


@pytest.mark.django_db
@patch("apps.proposals.services.send_email_notification.delay")
def test_reject_proposal(mock_send_email_notification, proposal_factory):
    proposal = proposal_factory()

    services.reject_proposal(proposal)

    proposal.refresh_from_db()
    assert proposal.status == Proposal.ProposalStatus.REJECTED
    mock_send_email_notification.assert_called_once()
