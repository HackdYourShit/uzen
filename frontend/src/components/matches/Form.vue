<template>
  <div>
    <div class="columns">
      <div class="column is-half">
        <b-field label="Rule ID">
          <b-input v-model="filters.ruleId"></b-input>
        </b-field>
      </div>
      <div class="column is-half">
        <b-field label="Snapshot ID">
          <b-input v-model="filters.snapshotId"></b-input>
        </b-field>
      </div>
    </div>
    <div class="columns">
      <div class="column is-half">
        <b-field label="From">
          <b-datetimepicker
            placeholder="Click to select..."
            icon="calendar-today"
            v-model="filters.fromAt"
            :datetime-formatter="datetimeFormatter"
          ></b-datetimepicker>
        </b-field>
      </div>
      <div class="column is-half">
        <b-field label="To">
          <b-datetimepicker
            placeholder="Click to select..."
            icon="calendar-today"
            v-model="filters.toAt"
            :datetime-formatter="datetimeFormatter"
          ></b-datetimepicker>
        </b-field>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Mixins } from "vue-mixin-decorator";
import { Prop } from "vue-property-decorator";

import {
  ErrorDialogMixin,
  SearchFormComponentMixin,
  SearchFormMixin,
} from "@/components/mixins";
import { MatchFilters } from "@/types";

@Component
export default class SearchForm extends Mixins<SearchFormComponentMixin>(
  ErrorDialogMixin,
  SearchFormMixin
) {
  @Prop() private ruleId: string | undefined;
  @Prop() private snapshotId: string | undefined;

  private filters: MatchFilters = {
    ruleId: this.ruleId,
    snapshotId: this.snapshotId,
    fromAt: undefined,
    toAt: undefined,
  };

  filtersParams() {
    const obj: { [k: string]: string | number | undefined } = {};

    for (const key in this.filters) {
      if (this.filters[key] !== undefined) {
        const value = this.filters[key];
        obj[key] = this.normalizeFilterValue(value);
      }
    }
    return obj;
  }
}
</script>
