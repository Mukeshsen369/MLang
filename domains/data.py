from domains.base import Domain, DomainResponse


class DataDomain(Domain):
    name = "DATA"

    def can_handle(self, context):
        raw = context["raw_input"].lower()
        return any(k in raw for k in [
            "find", "minimum", "maximum", "min", "max",
            "best", "sort",
            "where", "and", "or",
            "above", "below", "near", "around",
            "closest", "nearest",
            "highest", "lowest"
        ])

    def handle(self, context):
        raw = context["raw_input"].lower()

        # -------- COMPOUND PHRASES (TOP PRIORITY) --------
        if "highest below" in raw:
            return self._highest_below(raw, context)

        if "lowest above" in raw:
            return self._lowest_above(raw, context)

        if "closest above" in raw:
            return self._closest_above(raw, context)

        if "closest below" in raw:
            return self._closest_below(raw, context)

        # -------- CLOSEST / NEAREST --------
        if "closest" in raw or "nearest" in raw:
            return self._handle_closest(raw, context)

        # -------- NORMAL EXTRACTION + FILTERING --------
        numbers, reason = self._extract_and_filter(raw, context)
        if not numbers:
            return DomainResponse(True, needs_clarification=True)

        if "minimum" in raw or "min" in raw:
            result = min(numbers)
            context["last_decision"] = {
                "type": "data",
                "reason": f"After filtering, the smallest value in {numbers} is {result}. {reason}"
            }
            return DomainResponse(True, f"The minimum value is {result}.")

        if "maximum" in raw or "max" in raw:
            result = max(numbers)
            context["last_decision"] = {
                "type": "data",
                "reason": f"After filtering, the largest value in {numbers} is {result}. {reason}"
            }
            return DomainResponse(True, f"The maximum value is {result}.")

        if "best" in raw:
            result = max(numbers)
            context["last_decision"] = {
                "type": "data",
                "reason": f"After filtering, {result} is the highest value in {numbers}. {reason}"
            }
            return DomainResponse(True, f"The best value is {result}.")

        if "sort" in raw:
            sorted_vals = sorted(numbers)
            context["last_decision"] = {
                "type": "data",
                "reason": f"I sorted the values {numbers}."
            }
            return DomainResponse(True, f"The sorted result is {sorted_vals}.")

        return DomainResponse(False)

    # ==================================================
    # COMPOUND PHRASES
    # ==================================================
    def _highest_below(self, text, context):
        numbers, target = self._resolve_compound(text, context, "below")
        if target is None:
            return DomainResponse(True, needs_clarification=True)

        candidates = [v for v in numbers if v < target]
        if not candidates:
            return DomainResponse(True, needs_clarification=True)

        result = max(candidates)
        context["last_decision"] = {
            "type": "data",
            "reason": f"I selected the highest value below {target} from {numbers}."
        }
        return DomainResponse(True, f"The highest value below {target} is {result}.")

    def _lowest_above(self, text, context):
        numbers, target = self._resolve_compound(text, context, "above")
        if target is None:
            return DomainResponse(True, needs_clarification=True)

        candidates = [v for v in numbers if v > target]
        if not candidates:
            return DomainResponse(True, needs_clarification=True)

        result = min(candidates)
        context["last_decision"] = {
            "type": "data",
            "reason": f"I selected the lowest value above {target} from {numbers}."
        }
        return DomainResponse(True, f"The lowest value above {target} is {result}.")

    def _closest_above(self, text, context):
        numbers, target = self._resolve_compound(text, context, "above")
        if target is None:
            return DomainResponse(True, needs_clarification=True)

        candidates = [v for v in numbers if v > target]
        if not candidates:
            return DomainResponse(True, needs_clarification=True)

        result = min(candidates, key=lambda v: v - target)
        context["last_decision"] = {
            "type": "data",
            "reason": f"I chose the value just above {target}."
        }
        return DomainResponse(True, f"The closest value above {target} is {result}.")

    def _closest_below(self, text, context):
        numbers, target = self._resolve_compound(text, context, "below")
        if target is None:
            return DomainResponse(True, needs_clarification=True)

        candidates = [v for v in numbers if v < target]
        if not candidates:
            return DomainResponse(True, needs_clarification=True)

        result = max(candidates, key=lambda v: target - v)
        context["last_decision"] = {
            "type": "data",
            "reason": f"I chose the value just below {target}."
        }
        return DomainResponse(True, f"The closest value below {target} is {result}.")

    # ==================================================
    # GENERIC EXTRACTION + FILTERING
    # ==================================================
    def _extract_and_filter(self, text, context):
        data_store = context.get("data_store", {})
        numbers = []
        reason = "No filtering was applied."

        # Base extraction
        if " of " in text:
            name = text.split(" of ", 1)[1].split()[0]
            numbers = data_store.get(name, [])
        elif " in " in text:
            name = text.split(" in ", 1)[1].split()[0]
            numbers = data_store.get(name, [])
        else:
            for t in text.replace(",", " ").split():
                try:
                    numbers.append(float(t))
                except ValueError:
                    continue

        # Symbolic where
        if " where " in text:
            condition = text.split(" where ", 1)[1].strip()
            numbers, reason = self._apply_condition(numbers, condition, context)

        # Natural comparatives
        if " above " in text:
            rhs = self._resolve_rhs(text.split(" above ", 1)[1], context)
            numbers = [v for v in numbers if v > rhs]
            reason = f"I kept values above {rhs}."

        if " below " in text:
            rhs = self._resolve_rhs(text.split(" below ", 1)[1], context)
            numbers = [v for v in numbers if v < rhs]
            reason = f"I kept values below {rhs}."

        return numbers, reason

    def _apply_condition(self, numbers, condition, context):
        data_store = context.get("data_store", {})
        for op in [">=", "<=", ">", "<", "=="]:
            if op in condition:
                rhs = self._resolve_rhs(condition.split(op, 1)[1].strip(), context)
                if rhs is None:
                    return numbers, "Condition could not be resolved."
                if op == ">":
                    return [v for v in numbers if v > rhs], f"I kept values > {rhs}."
                if op == "<":
                    return [v for v in numbers if v < rhs], f"I kept values < {rhs}."
                if op == ">=":
                    return [v for v in numbers if v >= rhs], f"I kept values ≥ {rhs}."
                if op == "<=":
                    return [v for v in numbers if v <= rhs], f"I kept values ≤ {rhs}."
                if op == "==":
                    return [v for v in numbers if v == rhs], f"I kept values == {rhs}."
        return numbers, "No valid condition was applied."

    def _resolve_compound(self, text, context, word):
        data_store = context.get("data_store", {})
        numbers = []

        if " of " in text:
            dataset = text.split(" of ", 1)[1].strip()
            numbers = data_store.get(dataset, [])
        elif " in " in text:
            dataset = text.split(" in ", 1)[1].strip()
            numbers = data_store.get(dataset, [])

        target_part = text.split(word, 1)[1]
        for stop in [" of ", " in "]:
            if stop in target_part:
                target_part = target_part.split(stop, 1)[0]
        target_part = target_part.strip()

        if target_part in data_store:
            target = data_store[target_part][0]
        else:
            try:
                target = float(target_part)
            except ValueError:
                target = None

        return numbers, target

    def _handle_closest(self, text, context):
        data_store = context.get("data_store", {})
        if " to " not in text or " in " not in text:
            return DomainResponse(True, needs_clarification=True)

        target_part, dataset = text.split(" to ", 1)[1].split(" in ", 1)
        numbers = data_store.get(dataset.strip(), [])
        target = self._resolve_rhs(target_part.strip(), context)

        if target is None or not numbers:
            return DomainResponse(True, needs_clarification=True)

        closest = min(numbers, key=lambda v: (abs(v - target), v))
        context["last_decision"] = {
            "type": "data",
            "reason": f"I chose {closest} because it is closest to {target}."
        }
        return DomainResponse(True, f"The closest value is {closest}.")

    def _resolve_rhs(self, token, context):
        data_store = context.get("data_store", {})
        token = token.strip().split()[0]
        if token in data_store:
            return data_store[token][0]
        try:
            return float(token)
        except ValueError:
            return None
