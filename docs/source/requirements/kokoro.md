# Kokoro TTS Requirements

% SPDX-FileCopyrightText: 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>
% SPDX-License-Identifier: AGPL-3.0-only

% Part of the aquarion-libtts library of the Aquarion AI project.
% Copyright (C) 2025-present Krys Lawrence <aquarion.5.krystopher@spamgourmet.org>

% This program is free software: you can redistribute it and/or modify it under the
% terms of the GNU Affero General Public License as published by the Free Software
% Foundation, version 3.

% This program is distributed in the hope that it will be useful, but WITHOUT ANY
% WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
% PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

% You should have received a copy of the GNU Affero General Public License along with
% this program. If not, see <https://www.gnu.org/licenses/>.

The following are the
[BDD](https://en.wikipedia.org/wiki/Behavior-driven_development)-style requirements for
aquarion-libtts's [Kokoro TTS](https://huggingface.co/hexgrad/Kokoro-82M) backend.

```{literalinclude} ../../../tests/acceptance/features/kokoro.feature
:lines: 3-
:language: gherkin
```
