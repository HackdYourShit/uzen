<template>
  <div>
    <b-message type="is-warning">
      Perform oneshot analysis. The analysis results are not persistent.
    </b-message>

    <div class="box">
      <b-field label="URL">
        <b-input
          class="control is-expanded"
          placeholder="http://example.com"
          type="url"
          v-model="url"
        ></b-input>
      </b-field>

      <BasicYaraForm v-bind:source.sync="source" v-bind:target.sync="target" />

      <br />

      <div class="buttons is-centered">
        <b-button
          type="is-light"
          icon-pack="fas"
          icon-left="search"
          @click="scan"
          >Scan</b-button
        >
        <b-button
          type="is-info"
          icon-pack="fas"
          icon-left="cogs"
          @click="showOptions = !showOptions"
          >Options</b-button
        >
      </div>

      <Options
        v-if="showOptions"
        v-bind:acceptLanguage.sync="acceptLanguage"
        v-bind:host.sync="host"
        v-bind:ignoreHTTPSErrors.sync="ignoreHTTPSErrors"
        v-bind:referer.sync="referer"
        v-bind:timeout.sync="timeout"
        v-bind:userAgent.sync="userAgent"
      />
    </div>
    <div class="message">
      <b-message v-if="hasSnapshot()" :type="messageType()">
        {{ message() }}
      </b-message>
    </div>

    <div>
      <SnapshotComponent
        v-if="hasSnapshot()"
        v-bind:_snapshot="oneshot.snapshot"
        v-bind:yaraResult="yaraResult()"
      />
    </div>
  </div>
</template>

<script lang="ts">
import axios from "axios";
import { Component, Mixins } from "vue-mixin-decorator";

import { ErrorDialogMixin } from "@/components/mixins";
import Options from "@/components/snapshots/Options.vue";
import SnapshotComponent from "@/components/snapshots/Snapshot.vue";
import BasicYaraForm from "@/components/yara/BasicForm.vue";
import { ErrorData, Oneshot, TargetTypes, YaraResult } from "@/types";

@Component({
  components: {
    BasicYaraForm,
    SnapshotComponent,
    Options,
  },
})
export default class OneshotView extends Mixins<ErrorDialogMixin>(
  ErrorDialogMixin
) {
  private source = "";
  private target: TargetTypes = "body";
  private url = "";
  private oneshot: Oneshot | undefined = undefined;

  private showOptions = false;
  private acceptLanguage = "";
  private ignoreHTTPSErrors = false;
  private referer = "";
  private timeout = 30000;
  private userAgent = "";
  private host = "";

  async scan() {
    const loadingComponent = this.$buefy.loading.open({
      container: this.$el.firstElementChild,
    });

    try {
      const response = await axios.post<Oneshot>("/api/yara/oneshot", {
        source: this.source === "" ? undefined : this.source,
        url: this.url,
        target: this.target,
        acceptLanguage:
          this.acceptLanguage === "" ? undefined : this.acceptLanguage,
        host: this.host === "" ? undefined : this.host,
        ignoreHttpErrors: this.ignoreHTTPSErrors,
        referer: this.referer === "" ? undefined : this.referer,
        timeout: this.timeout,
        userAgent: this.userAgent === "" ? undefined : this.userAgent,
      });

      this.oneshot = response.data;

      loadingComponent.close();

      this.$forceUpdate();
    } catch (error) {
      loadingComponent.close();

      const data = error.response.data as ErrorData;
      this.alertError(data);
    }
  }

  hasSnapshot(): boolean {
    return this.oneshot?.snapshot !== undefined;
  }

  matched(): boolean {
    if (this.oneshot?.matched === undefined) {
      return false;
    }
    return this.oneshot.matched;
  }

  message(): string {
    if (this.matched()) {
      return "Matched with YARA rule";
    }
    return "Not matched with YARA rule";
  }

  messageType(): string {
    if (this.matched()) {
      return "is-warning";
    }
    return "is-success";
  }

  yaraResult(): YaraResult | undefined {
    if (this.oneshot?.matches !== undefined) {
      const result: YaraResult = {
        snapshotId: "",
        scriptId: undefined,
        target: this.target,
        matches: this.oneshot.matches,
      };
      return result;
    }
    return undefined;
  }
}
</script>
