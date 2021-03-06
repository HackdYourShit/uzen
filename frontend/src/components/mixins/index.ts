import { ErrorDialogMixin } from "./error_dialog";
import { HighlightMixin } from "./highlight";
import { SearchFormMixin } from "./search_form";

export interface SearchFormComponentMixin
  extends SearchFormMixin,
    ErrorDialogMixin {}

export interface HighlightComponentMixin
  extends HighlightMixin,
    ErrorDialogMixin {}

export { ErrorDialogMixin, HighlightMixin, SearchFormMixin };
