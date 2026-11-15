"""How a person signs in to a profile.

Every sign-in method is an AuthProvider that returns an AuthIdentity (provider name +
the provider's stable user id). Profiles keep a list of such identities
(profiles.link_identity), and storage can find a profile by one
(Repository.find_profile_by_identity).

Now only LocalAuth exists: a profile on this computer, optionally locked with a PIN.
Planned providers plug in here without changing profiles or storage:

* GoogleAuth — OAuth 2.0 + PKCE; on desktop the system browser with a loopback
  redirect (http://127.0.0.1:<port>), on iOS the Google Sign-In SDK. Identity
  subject = the ID token's "sub" claim.
* AppleAuth — Sign in with Apple; native on iOS/macOS, web flow (Services ID) on
  Windows. Apple sends the name only on the FIRST sign-in and may give a private
  relay e-mail, so the name is stored in the profile and e-mail is never a key.
"""

import abc
from dataclasses import dataclass
from typing import Optional


class AuthError(RuntimeError):
    """Sign-in failed; the message is shown to the user (Ukrainian)."""


@dataclass
class AuthIdentity:
    provider: str
    subject: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture_url: Optional[str] = None


class AuthProvider(abc.ABC):
    #: Provider key stored in profile identities ("local", "google", "apple").
    id = ""
    #: Button title in the "Як увійти?" step.
    title = ""
    icon = ""

    def is_available(self):
        """Whether this method can be offered on this device/build."""
        return True

    @abc.abstractmethod
    def sign_in(self, **kwargs):
        """Runs the sign-in flow and returns an AuthIdentity (raises AuthError)."""


def available_providers():
    """Sign-in methods offered when a profile is created, in display order."""
    from .local import LocalAuth

    providers = [LocalAuth()]
    return [p for p in providers if p.is_available()]
