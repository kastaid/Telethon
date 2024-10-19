from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional, Sequence

from typing_extensions import Self

from ....session import ChannelRef, GroupRef
from ....tl import abcs, types
from ..chat_restriction import ChatRestriction
from ..meta import NoPublicConstructor
from .peer import Peer

if TYPE_CHECKING:
    from ...client.client import Client


class Group(Peer, metaclass=NoPublicConstructor):
    """
    A small group or supergroup.

    You can get a group from messages via :attr:`telethon.types.Message.chat`,
    or from methods such as :meth:`telethon.Client.resolve_username`.
    """

    def __init__(
        self,
        client: Client,
        chat: (
            types.ChatEmpty
            | types.Chat
            | types.ChatForbidden
            | types.Channel
            | types.ChannelForbidden
        ),
    ) -> None:
        self._client = client
        self._raw = chat

    @classmethod
    def _from_raw(cls, client: Client, chat: abcs.Chat) -> Self:
        if isinstance(chat, (types.ChatEmpty, types.Chat, types.ChatForbidden)):
            return cls._create(client, chat)
        elif isinstance(chat, (types.Channel, types.ChannelForbidden)):
            if chat.broadcast:
                raise RuntimeError("cannot create group from broadcast channel")
            return cls._create(client, chat)
        else:
            raise RuntimeError("unexpected case")

    # region Overrides

    @property
    def id(self) -> int:
        return self._raw.id

    @property
    def name(self) -> str:
        """
        The group's title.

        This property is always present, but may be the empty string.
        """
        return getattr(self._raw, "title", None) or ""

    @property
    def username(self) -> Optional[str]:
        return getattr(self._raw, "username", None)

    @property
    def ref(self) -> GroupRef | ChannelRef:
        if isinstance(self._raw, (types.ChatEmpty, types.Chat, types.ChatForbidden)):
            return GroupRef(self._raw.id, None)
        else:
            return ChannelRef(self._raw.id, self._raw.access_hash)

    @property
    def _ref(self) -> GroupRef | ChannelRef:
        return self.ref

    # endregion Overrides

    @property
    def is_megagroup(self) -> bool:
        """
        Whether the group is a supergroup.

        These are known as "megagroups" in Telegram's API, and are different from "gigagroups".
        """
        return isinstance(self._raw, (types.Channel, types.ChannelForbidden))

    async def set_default_restrictions(
        self,
        restrictions: Sequence[ChatRestriction],
        *,
        until: Optional[datetime.datetime] = None,
    ) -> None:
        """
        Alias for :meth:`telethon.Client.set_chat_default_restrictions`.
        """
        await self._client.set_chat_default_restrictions(
            self, restrictions, until=until
        )