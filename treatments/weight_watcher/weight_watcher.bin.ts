({

  main: async function(api){
    await api.llm.addSystemContext(this.getSystemMessage())





    const response = await api.llm.sendMessage("Hi this is my data so far: " + JSON.stringify(api.data) + ", how am i doing?")






    return {
      message: response
    }

  },
  
  getSystemMessage: function(){
    return `
      You are an assistant that is helping the user with their weight.
      They will send you data that has both the date and record value for step counts and body mass.
      Keep it short in your response.
    `
  }

})