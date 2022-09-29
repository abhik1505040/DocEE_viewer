<script lang="ts">
  import { Streamlit } from "./streamlit";
  import type { RenderData } from "./streamlit";
  import MarkedWord from "./components/MarkedWord.svelte";
  import { onMount, afterUpdate, onDestroy } from "svelte"

  let text: string = "";
  let ents: {
    start: number;
    end: number;
    label: string;
  }[] = [];
  export let header: string;
  export let disabled: boolean;
  
  const onRender = (event: Event): void => {
    const data = (event as CustomEvent<RenderData>).detail;
    header = data.args["header"];
    text = data.args["text"];
    ents = data.args["ents"];
    
  };

  onMount(() => {
    Streamlit.setComponentReady();
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
    Streamlit.setFrameHeight();
  });

  afterUpdate(() => {
    Streamlit.setFrameHeight();
  });

  onDestroy(() => {
    Streamlit.events.removeEventListener(Streamlit.RENDER_EVENT, onRender);
  });

</script>

<main {disabled}>
  <h4>{header}</h4>
  {#each ents as { start, end, label }, i (start)}
    {#if i == 0}<span class={i}>{text.substring(0, start)}</span>{/if}
    <MarkedWord
      words={text.substring(start, end)}
      {label}
      id={i}
      start={start}
      end={end}
    />
    {#if i != ents.length - 1}
      <span class={i+1}>{text.substring(end, ents[i + 1]["start"])}</span>
    {/if}
    {#if i == ents.length - 1}<span class={i+1}>{text.substring(end)}</span>{/if}
  {:else}
    {text}
  {/each}
</main>

<style>
  main {
    padding: 1em;
    line-height: 2;
    font-family: "Source Sans Pro", sans-serif;
  }
</style>
