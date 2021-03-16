# camera-app


<p align="middle">
 <img src="etc/input2.png" title="특정 User 예제" width="25%" height="auto" ></img>
 <img src="etc/input3.png" title="특정 User 예제" width="25%" height="auto" ></img>
 <img src="etc/input4.png" title="특정 User 예제" width="25%" height="auto" ></img>
 <img src="etc/input5.png" title="특정 User 예제" width="25%" height="auto" ></img>
</p>



<template>
  <figure>
    <img :src="etc/input2.png" alt=""/>
    <figcaption>Legenda: {{ caption }} - {{ src }}</figcaption>
  </figure>
</template>
<script>
export default {
  props: ['src', 'caption'],
  computed: {
    imagesrc () {
      return './images/' + this.src
    }
  }
}
</script>
